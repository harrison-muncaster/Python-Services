import os
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from utils.movies import MovieDatabaseAPI
from utils.views import home_view, movie_modal_view, movie_info_message_view


SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN_DEMO')
SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN_DEMO')
SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET_DEMO')

logging.basicConfig(level=logging.ERROR)

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SIGNING_SECRET
)


@app.event('app_home_opened')
def update_home_view(ack, client, event, logger):
    """Publish App Home View."""
    ack()
    view = home_view()
    try:
        client.views_publish(
            user_id=event['user'],
            view=view
        )
    except Exception as e:
        logger.error(e)


@app.action('select_a_movie')
def open_movie_selection_modal(ack, client, body, logger):
    """Open Modal Movie Selection View. """
    ack()
    view = movie_modal_view()
    try:
        client.views_open(
            trigger_id=body['trigger_id'],
            view=view
        )
    except Exception as e:
        logger.error(e)


@app.options('movie_typeahead')
def get_movie_typeahead_list(ack, body):
    """Populate Movie List for Dropdown Modal Menu."""
    title_input = body['value']
    movie_db = MovieDatabaseAPI()
    options = movie_db.filter_movies_by_title(title_input)
    ack(options=options)


@app.view('movie_select_view')
def send_movie_info_message(ack, client, body, view, logger):
    """Send Movie Info Message to User."""
    ack()
    user_id = body['user']['id']
    movie_db = MovieDatabaseAPI()
    movie_id = view['state']['values']['comments']['movie_typeahead']['selected_option']['value']
    movie_info = movie_db.get_movie_by_id(movie_id)
    msg_view = movie_info_message_view(movie_info)
    try:
        client.chat_postMessage(channel=user_id, blocks=msg_view, text='Movie Info!')
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
