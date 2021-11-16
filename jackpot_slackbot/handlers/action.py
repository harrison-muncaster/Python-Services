import tornado

import bf_logging
from bf_rig import settings
from handlers.base import BaseHandler
from utils.slack import ActionRequest, SlackAPI
from utils.spinner import Spinner
from utils.views import MessageView


SLACK_BOT_TOKEN = settings.get('slack_bot_token')
SLACK_SIGNING_SECRET = settings.get('slack_signing_secret')

logger = bf_logging.Log()


class ActionHandler(BaseHandler):
    async def post(self):
        """Payload Received from Action Request in Slack.
        """

        # Initialize SlackAPI Client & Action Request Object
        slack = SlackAPI(SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET)
        action = ActionRequest(self.request.body.decode('utf-8'))

        # Verify Request came from Slack & Send Response back to Slack
        slack.is_valid_request(self.request)
        self.finish()

        views = MessageView(action=action)

        if action.interactive_action_id == 'click_me_button':
            logger.info(f'Action Request Received from {action.user_name}.')
            slack.update_message(action.channel_id, action.message_ts, views.start_spinning())

        elif 'wildcard_button_' in action.interactive_action_id:
            spinner = Spinner(action.blocks)

            # Only allow player that clicked SPIN button to play & change emojis
            if action.user_id == spinner.player_id:
                emoji_to_replace = None

                if action.interactive_action_id == 'wildcard_button_one':
                    if spinner.emoji_one == spinner.is_spinning:
                        emoji_to_replace = spinner.emoji_positions[0]

                elif action.interactive_action_id == 'wildcard_button_two':
                    if spinner.emoji_two == spinner.is_spinning:
                        emoji_to_replace = spinner.emoji_positions[1]

                elif action.interactive_action_id == 'wildcard_button_three':
                    if spinner.emoji_three == spinner.is_spinning:
                        emoji_to_replace = spinner.emoji_positions[2]

                elif action.interactive_action_id == 'wildcard_button_four':
                    if spinner.emoji_four == spinner.is_spinning:
                        emoji_to_replace = spinner.emoji_positions[3]

                elif action.interactive_action_id == 'wildcard_button_five':
                    if spinner.emoji_five == spinner.is_spinning:
                        emoji_to_replace = spinner.emoji_positions[4]

                if emoji_to_replace:
                    view = views.update_spinner_emoji(spinner, emoji_to_replace)
                    updated_msg = slack.update_message(action.channel_id, action.message_ts, view)

                    if spinner.is_on_last_spin:
                        if spinner.win_count == 1:
                            msg_view = views.loser(updated_msg['message']['blocks'])
                        elif spinner.win_count == 2:
                            msg_view = views.winner(updated_msg['message']['blocks'], 2)
                        elif spinner.win_count == 3:
                            msg_view = views.winner(updated_msg['message']['blocks'], 3)
                        elif spinner.win_count == 4:
                            msg_view = views.winner(updated_msg['message']['blocks'], 4)
                        else:
                            msg_view = views.jackpot(updated_msg['message']['blocks'])

                        slack.update_message(action.channel_id, action.message_ts, msg_view)

                        # If losing game, Delete message after 15 sec
                        if spinner.win_count == 1:
                            await tornado.gen.sleep(15)
                            slack.delete_message(action.channel_id, action.message_ts)
