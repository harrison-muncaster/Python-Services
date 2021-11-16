import bf_logging
from bf_rig import settings
from handlers.base import BaseHandler
from utils.slack import SlackAPI, SlashRequest
from utils.views import MessageView
from utils.slack import SlackInputValidationError

INVALID_CMD_MSG = settings.get('invalid_cmd_msg')
SLACK_BOT_TOKEN = settings.get('slack_bot_token')
SLACK_SIGNING_SECRET = settings.get('slack_signing_secret')

logger = bf_logging.Log()


class SlashHandler(BaseHandler):
    def post(self):
        """Payload Received from Slash Request in Slack.
        """

        # Initialize SlackAPI Client & Slash Request Object
        slack = SlackAPI(SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET)
        slash = SlashRequest(self.request.body.decode('utf-8'))

        # Verify Request came from Slack & Send Response Back to Slack
        slack.is_valid_request(self.request)
        self.finish()

        logger.info(f'Slash Request Received from {slash.user_name}.')
        try:
            slash.is_valid_input(slash.target_user)
        except SlackInputValidationError:
            logger.debug('Invalid Input')
            slack.send_ephemeral_message(slash.channel_id, slash.user_id, text=INVALID_CMD_MSG)
            return
        else:
            # Build Message Schema & Send Game Message
            views = MessageView(slash)
            slack.send_message(slash.channel_id, views.start_no_spin())
