import requests
import json
import os

from functools import cached_property
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse
from slack_sdk.errors import SlackApiError


class Slack:
    """Class representing the Slack API."""
    def __init__(self, oauth_token: str, bot_token: str) -> None:
        self.slack_bot = WebClient(token=bot_token)
        self.slack_oauth = WebClient(token=oauth_token)
        self.webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

    def api_test(self) -> Optional[SlackResponse]:
        """Verify authentication with Slack & API token validity."""
        try:
            response = self.slack_oauth.api_test()
            response = self.slack_bot.api_test()
        except SlackApiError as e:
            response = None
        return response

    @cached_property
    def users(self) -> Optional[list[dict]]:
        """Get all users in the Slack workspace."""
        try:
            response = self.slack_bot.users_list(limit=400)
            users = response['members']
            while response['response_metadata'].get('next_cursor'):
                next_cursor = response['response_metadata']['next_cursor']
                response = self.slack_bot.users_list(limit=400, cursor=next_cursor)
                users.extend(response['members'])
        except SlackApiError as e:
            users = None
        return users

    def get_group_members(self, group_id: str) -> Optional[list[str]]:
        """Get all members of specified Slack group."""
        try:
            response = self.slack_bot.usergroups_users_list(usergroup=group_id)
        except SlackApiError as e:
            users = None
        else:
            users = response['users']
        return users

    def update_group_members(self, group_id: str, users: list[str]) -> Optional[SlackResponse]:
        """Set members of specified Slack group to specific list of users."""
        try:
            response = self.slack_oauth.usergroups_users_update(usergroup=group_id, users=users)
        except SlackApiError as e:
            response = None
        return response

    def send_webhook_alert(self, msg: str) -> None:
        """Send Webhook alert message to EntApps Alerts channel."""
        message = {'text': msg}
        response = requests.post(self.webhook_url, data=json.dumps(message))
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f'Slack Alert failed to send!\n'
                  f'{e}')
