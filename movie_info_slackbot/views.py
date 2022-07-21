from datetime import datetime
import os

from slack_sdk.models.blocks import (
    ActionsBlock,
    ButtonElement,
    ContextBlock,
    ExternalDataSelectElement,
    HeaderBlock,
    ImageElement,
    InputBlock,
    MarkdownTextObject,
    SectionBlock
)
from slack_sdk.models.views import View

MOVIE_IMAGE_BASE_URL = os.environ.get('MOVIE_DATABASE_IMAGE_URL')


def home_view() -> View:
    """Return Home View Object."""
    blocks = [
        HeaderBlock(
            text='Welcome to Movie Info :clapper:'
        ).to_dict(),
        SectionBlock(
            text=MarkdownTextObject(
                text='_Click the button below to pick a movie!_'
            )
        ).to_dict(),
        ActionsBlock(
            block_id='home_view',
            elements=[
                ButtonElement(
                    text='Select a Movie!',
                    action_id='select_a_movie'
                )
            ]
        ).to_dict()
    ]
    view = View(
        type='home',
        callback_id='home_view',
        blocks=blocks
    )
    return view


def movie_modal_view() -> View:
    """Return Modal Movie Selection View Object."""
    blocks = [
        InputBlock(
            label='Select a Movie!',
            block_id='comments',
            element=ExternalDataSelectElement(
                placeholder='Start Typing...',
                action_id='movie_typeahead',
                min_query_length=3
            )
        ).to_dict()
    ]
    view = View(
        type='modal',
        title=':clapper: Movie Info',
        submit='Submit',
        close='Cancel',
        callback_id='movie_select_view',
        blocks=blocks
    )
    return view


def movie_info_message_view(movie_info: dict) -> list:
    """Return Movie Info Message Blocks."""
    formatted_date = datetime.strptime(movie_info['release_date'], '%Y-%m-%d').strftime('%B %d, %Y')
    blocks = [
        SectionBlock(
            text=MarkdownTextObject(
                text='Here\'s the movie info you requested!'
            )
        ).to_dict(),
        HeaderBlock(
            text=f'{movie_info["title"]}'
        ).to_dict(),
        ContextBlock(
            elements=[
                MarkdownTextObject(
                    text=f'*Release Date:* {formatted_date}'
                )
            ]
        ).to_dict(),
        SectionBlock(
            text=MarkdownTextObject(
                text=movie_info['overview']
            ),
            accessory=ImageElement(
                image_url=f'{MOVIE_IMAGE_BASE_URL}{movie_info["poster_path"]}',
                alt_text=movie_info['tagline']
            )
        ).to_dict()
    ]
    return blocks
