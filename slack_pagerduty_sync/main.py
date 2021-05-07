import os
import smtplib
import csv

from smtplib import SMTPResponseException

from slack_api import Slack
from pagerduty import PagerDuty
from dodgeball import Dodgeball


SLACK_OAUTH_TOKEN = os.environ.get('SLACK_OAUTH_TOKEN')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
PAGERDUTY_TOKEN = os.environ.get('PAGERDUTY_TOKEN')


def send_email_alert(body):
    """Send alert email to EntApps."""
    sender = os.environ.get('SENDER')
    recipient = os.environ.get('RECIPIENT')
    subject = 'Slack / PD Group Sync Issue'
    smtp_host = os.environ.get('SMTPHOST')
    message = f'Subject:{subject}\n\n{body}'
    with smtplib.SMTP(smtp_host) as server:
        try:
            server.starttls()
            server.sendmail(sender, recipient, message)
        except (SMTPResponseException, Exception) as e:
            print('Alert Email could not be sent!\n'
                  f'{e}')


try:
    with open('groups.csv', 'rt', encoding='utf-8-sig') as groups_csv_data:
        GROUPS_CSV = csv.DictReader(groups_csv_data)
        ONCALL_GROUPS = [group for group in GROUPS_CSV]

    with open('groups_to_ignore.csv') as ignore_csv_data:
        IGNORE_CSV = csv.reader(ignore_csv_data)
        POLICIES_TO_IGNORE = [group[0] for group in IGNORE_CSV]

except FileNotFoundError as e:
    send_email_alert(e)
    raise SystemError(e)


def main():
    """Sync users from Pagerduty policies / Dodgeball groups to Slack on-call groups."""

    # Initialize our Slack, PagerDuty, & Dodgeball Objects
    slack = Slack(SLACK_OAUTH_TOKEN, SLACK_BOT_TOKEN)
    pagerduty = PagerDuty(PAGERDUTY_TOKEN)
    dodgeball = Dodgeball()

    # Validate API/token connectivity with PagerDuty
    if not pagerduty.api_test():
        error_message = (
            'Slack/PD Group Sync Failure:\n'
            'Could not authenticate with PagerDuty!\n'
            'Please ensure PagerDuty API token is valid.\n'
            'Script exited without running. Investigate immediately!'
        )
        send_email_alert(error_message)
        slack.send_webhook_alert(error_message)
        raise SystemError(error_message)

    # Validate API/token connectivity with Slack
    if not slack.api_test():
        error_message = (
            'Slack/PD Group Sync Failure:\n'
            'Could not authenticate with Slack!\n'
            'Please ensure Slack API tokens are valid.\n'
            'Script exited without running. Investigate immediately!'
        )
        send_email_alert(error_message)
        slack.send_webhook_alert(error_message)
        raise SystemError(error_message)

    # Validate slack.users property is populated
    if not slack.users or len(slack.users) < 15_000:
        error_users_count = 0 if not slack.users else len(slack.users)
        error_message = (
            'Slack/PD Group Sync Failure:\n'
            f'Insufficient data for Slack Users. User Count: {error_users_count}\n'
            'Script exited without running. Investigate immediately!'
        )
        send_email_alert(error_message)
        slack.send_webhook_alert(error_message)
        raise SystemError(error_message)

    counter = 1
    # Iterate through each on-call group and update members as necessary
    for group in ONCALL_GROUPS:

        print(f'\nProcessing Group #{counter} of {len(ONCALL_GROUPS)} Groups...')
        counter += 1

        # Get list of currently on-call users for specified PD Policy & Escalation level
        if group['source'].lower() == 'pagerduty':
            try:
                depth_as_int = int(group['depth'])
            except (ValueError, TypeError) as e:
                # if depth is null or non-numeric value then depth will default to 1
                depth_as_int = 1

            current_oncall_users = pagerduty.get_oncall_users(group['pagerduty_policy_id'], depth_as_int)

            if not current_oncall_users and group['pagerduty_policy_id'] not in POLICIES_TO_IGNORE:
                error_message = (
                    'Slack/PD Group Sync Issue:\n'
                    f'Slack Group: {group["slack_group_name"]}\n'
                    f'Issue: No users currently oncall for Pagerduty Policy {group["pagerduty_policy_id"]}.\n'
                    'Slack Oncall Group not updated.'
                )
                send_email_alert(error_message)
                slack.send_webhook_alert(error_message)
                print(error_message)
                continue

            elif not current_oncall_users and group['pagerduty_policy_id'] in POLICIES_TO_IGNORE:
                error_message = (
                    f'Slack Group: {group["slack_group_name"]}\n'
                    f'Issue: Group is on the ignore list and there is currently a gap in the schedule.\n'
                    'Slack Oncall Group not updated.'
                )
                print(error_message)
                continue

        # Get list of users from specified Dodgeball group
        elif group['source'].lower() == 'dodgeball':
            current_oncall_users = dodgeball.get_group_members(group['dodgeball_group'])

            if not current_oncall_users and group['dodgeball_group'] not in POLICIES_TO_IGNORE:
                error_message = (
                    'Slack/PD Group Sync Issue:\n'
                    f'Slack Group: {group["slack_group_name"]}\n'
                    f'Issue: No users in Dodgeball Group {group["dodgeball_group"]}.\n'
                    'Slack Oncall Group not updated.'
                )
                send_email_alert(error_message)
                slack.send_webhook_alert(error_message)
                print(error_message)
                continue

            elif not current_oncall_users and group['dodgeball_group'] in POLICIES_TO_IGNORE:
                error_message = (
                    f'Slack Group: {group["slack_group_name"]}\n'
                    f'Issue: Group is on the ignore list and there is currently a gap in the schedule.\n'
                    'Slack Oncall Group not updated.'
                )
                print(error_message)
                continue

        else:
            error_message = (
                'Slack/PD Group Sync Issue:\n'
                f'Slack Group: {group["slack_group_name"]}\n'
                f'Issue: Invalid source listed for group. Must be pagerduty or dodgeball NOT ({group["source"]}).\n'
                'Slack Oncall Group not updated.'
            )
            send_email_alert(error_message)
            slack.send_webhook_alert(error_message)
            print(error_message)
            continue

        # Get Slack user ID's from emails for oncall users
        users_to_add = []
        while len(users_to_add) < len(current_oncall_users):
            for user in slack.users:
                if user['profile'].get('email') and user['profile']['email'].lower() in current_oncall_users:
                    users_to_add.append(user['id'])
            break

        if not users_to_add:
            error_message = (
                'Slack/PD Group Sync Issue:\n'
                f'Slack Group: {group["slack_group_name"]}\n'
                f'Issue: Oncall users could not be found in the Slack workspace.\n'
                f'Users: {", ".join(current_oncall_users)}\n'
                'Slack Oncall Group not updated.'
            )
            send_email_alert(error_message)
            slack.send_webhook_alert(error_message)
            print(error_message)
            continue

        if len(users_to_add) < len(current_oncall_users):
            non_error_users = [
                user['profile']['email'].lower() for user in slack.users
                if user['profile'].get('email') and
                user['profile']['email'].lower() in current_oncall_users
            ]
            error_users = list(set(current_oncall_users) - set(non_error_users))
            error_message = (
                'Slack/PD Group Sync Issue:\n'
                f'Slack Group: {group["slack_group_name"]}\n'
                f'Source: {group["source"]}\n'
                f'Issue: The following oncall user(s) could not be found in the Slack Workspace. '
                f'The group will still update with the remaining users. Please remediate user issue.\n'
                f'User(s): {", ".join(error_users)}'
            )
            send_email_alert(error_message)
            slack.send_webhook_alert(error_message)
            print(f'{error_message}\n'
                  f'---------------------------------')

        # Update Slack oncall group with list of currently oncall users
        update_group_resp = slack.update_group_members(group['slack_group_id'], users_to_add)

        if not update_group_resp:
            error_message = (
                'Slack/PD Group Sync Issue:\n'
                f'Slack Group: {group["slack_group_name"]}\n'
                'Issue: Slack could not update oncall group with current oncall users.\n'
                'Slack Oncall Group not updated.'
            )
            send_email_alert(error_message)
            slack.send_webhook_alert(error_message)
            print(error_message)
            continue

        # Slack group successfully updated with oncall users
        print(f'Slack Group: {group["slack_group_name"]}\n'
              f'Source: {group["source"]}\n'
              f'Users: {", ".join(current_oncall_users)}\n'
              f'Status: Successfully updated Slack group!')


if __name__ == '__main__':
    main()
