import json
from urllib import parse

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
import tornado

import bf_logging


logger = bf_logging.Log()


class SlackInputValidationError(Exception):
    pass


class SlackValidator:
    """Class Representing Slack Validators."""

    def __init__(self, signing_secret: str = None) -> None:
        self.sig_verifier = SignatureVerifier(signing_secret)

    @staticmethod
    def is_valid_input(user_input: str) -> None:
        """Raise Input Error if User Input is Not a Slack User ID."""
        if user_input:
            chars = list(user_input)
            if chars[0] != '<' and chars[1] != '@' and chars[-1] != '>':
                raise SlackInputValidationError()
        else:
            raise SlackInputValidationError('Invalid Slash Command Input.')

    def is_valid_request(self, request: tornado.httputil.HTTPServerRequest) -> None:
        """Raise HTTP Error if Request is Not Valid Slack Request."""
        if not self.sig_verifier.is_valid_request(request.body, request.headers):
            logger.warning(f'Unauthorized Action Request Received\n{request.body.decode("utf-8")}')
            raise tornado.web.HTTPError(403, 'Forbidden')


class SlackAPI(SlackValidator):
    """Class Representing Slack's API."""

    def __init__(self, bot_token: str, signing_secret: str) -> None:
        self.slack = WebClient(token=bot_token)
        super().__init__(signing_secret)

    def send_message(self, channel_id: str, blocks: list, ts: str = None, text: str = None) -> dict:
        """Send Slack Message to Channel/Convo."""
        try:
            response = self.slack.chat_postMessage(channel=channel_id, blocks=blocks, thread_ts=ts, text=text)
        except SlackApiError:
            logger.exception(f'Could Not Send Message to Channel/Convo ID {channel_id}.')
        else:
            logger.debug(f'**Slack Message Sent to Channel/Convo ID {channel_id}**')
            return response

    def send_ephemeral_message(self, channel_id: str, user_id: str, text: str) -> dict:
        """Send Slack Ephemeral Message to User."""
        try:
            response = self.slack.chat_postEphemeral(channel=channel_id, user=user_id, text=text)
        except SlackApiError:
            logger.exception(f'Could Not Send Ephemeral Message to User ID {user_id}.')
        else:
            logger.debug(f'**Slack Ephemeral Message Sent to User ID {user_id}**')
            return response

    def update_message(self, channel_id: str, ts: str, blocks: list, as_user: bool = True) -> dict:
        """Update Specified Slack Message."""
        try:
            response = self.slack.chat_update(channel=channel_id, ts=ts, blocks=blocks, as_user=as_user)
        except SlackApiError:
            logger.exception(f'Could Not Update Slack Message #{ts}')
        else:
            logger.debug(f'**Slack Message #{ts} Updated**')
            return response

    def delete_message(self, channel_id: str, ts: str) -> dict:
        """Delete Specified Slack Message."""
        try:
            response = self.slack.chat_delete(channel=channel_id, ts=ts)
        except SlackApiError:
            logger.exception(f'Could Not Delete Slack Message #{ts}')
        else:
            logger.debug(f'**Slack Message #{ts} Deleted**')
            return response


class SlashRequest(SlackValidator):
    """Slash Request Payload."""

    def __init__(self, raw_post) -> None:
        self._post = parse.parse_qs(raw_post)
        super().__init__()

    @property
    def trigger_id(self) -> str:
        return self._post['trigger_id'][0]

    @property
    def channel_id(self) -> str:
        return self._post['channel_id'][0]

    @property
    def channel_name(self) -> str:
        return self._post['channel_name'][0]

    @property
    def user_name(self) -> str:
        return self._post['user_name'][0]

    @property
    def user_id(self) -> str:
        return self._post['user_id'][0]

    @property
    def target_user(self):
        return self._post['text'][0] if self._post.get('text') else None


class ActionRequest(SlackValidator):
    """Action Request Payload."""

    def __init__(self, raw_post) -> None:
        self._post = json.loads(dict(parse.parse_qsl(raw_post))['payload'])
        self._input = self._post['view']['state']['values'] if self._post.get('view') else None
        self._actions = self._post['actions'] if self._post.get('actions') else None
        super().__init__()

    @property
    def type(self) -> str:
        return self._post['type']

    @property
    def container_type(self) -> str:
        return self._post['container']['type']

    @property
    def user_id(self) -> str:
        return self._post['user']['id']

    @property
    def user_name(self) -> str:
        return self._post['user']['username']

    @property
    def trigger_id(self) -> str:
        return self._post['trigger_id']

    @property
    def response_url(self) -> str:
        return self._post['response_url']

    @property
    def interactive_type(self) -> str:
        return self._actions[0]['type'] if self._actions else None

    @property
    def interactive_action_id(self) -> str:
        return self._actions[0]['action_id'] if self._actions else None

    @property
    def interactive_block_id(self) -> str:
        return self._actions[0]['block_id'] if self._actions else None

    @property
    def interactive_selected_date(self) -> str:
        return self._actions[0]['selected_date'] if self._actions else None

    @property
    def message_ts(self) -> str:
        return self._post['message']['ts'] if self._post.get('message') else None

    @property
    def channel_id(self) -> str:
        return self._post['channel']['id'] if self._post.get('channel') else None

    @property
    def blocks(self) -> list:
        return self._post['message']['blocks'] if self._post.get('message') else None
