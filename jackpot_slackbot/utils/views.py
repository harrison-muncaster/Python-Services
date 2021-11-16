import copy
import random

from slack_sdk.models.blocks import (
    ActionsBlock,
    ButtonElement,
    DividerBlock,
    HeaderBlock,
    MarkdownTextObject,
    SectionBlock
)

from bf_rig import settings
from utils.slack import ActionRequest, SlashRequest
from utils.spinner import Spinner


EMOJIS = settings.get('emojis')
GAME_OVER_MSGS = settings.get('game_over_msgs')
TWO_MATCHES = settings.get('two_matches')
THREE_MATCHES = settings.get('three_matches')
JACKPOT_MSG = settings.get('jackpot_msg')

PARTY_UP_ARROW = EMOJIS['party_up_arrow']
UNICORN_SPIN = EMOJIS['unicorn_spin']
SHINY_WEED = EMOJIS['shiny_weed']
PARTY_TP = EMOJIS['party_tp']
PARTY_CAT = EMOJIS['party_cat']
CAT_SPIN = EMOJIS['cat_spin']
CAT_NO_SPIN = EMOJIS['cat_no_spin']
CHERRY_GALAXY = EMOJIS['cherry_galaxy']
GOLD_COINS = EMOJIS['gold_coins']
SHINY_DOLLAR = EMOJIS['shiny_dollar']
SPACE_CAT = EMOJIS['space_cat']
SHINY_SEVEN = EMOJIS['shiny_seven']
MONEY_MOUTH = EMOJIS['money_mouth']
WHITE_DIAMOND = EMOJIS['white_diamond']
PURPLE_DIAMOND = EMOJIS['purple_diamond']
RED_RUBY = EMOJIS['red_ruby']
WHITE_PURPLE = f'{WHITE_DIAMOND} {PURPLE_DIAMOND} '
WHITE_RED_PURPLE_RED = f'{WHITE_DIAMOND} {RED_RUBY} {PURPLE_DIAMOND} {RED_RUBY} '


class MessageView:
    """Class Representing Available Views for Slack Messages."""

    def __init__(self, slash: SlashRequest = None, action: ActionRequest = None) -> None:
        self.action = action
        self.slash = slash

    def start_no_spin(self) -> list:
        """Return Required Schema for Initial Message View."""
        blocks = [
            HeaderBlock(
                text=f'{GOLD_COINS} Are you feeling lucky?'
            ).to_dict(),
            SectionBlock(
                text=MarkdownTextObject(
                    text=(
                        f'{SHINY_DOLLAR * 5} *Jackpot:* _$100_\n'
                        f'{SHINY_DOLLAR * 4} *4x:* _$75_\n'
                        f'{SHINY_DOLLAR * 3} *3x:* _free lunch_\n'
                        f'{SHINY_DOLLAR * 2} *2x* _a surprise_'
                    )
                )
            ).to_dict(),
            SectionBlock(
                block_id='click_me_button_header',
                text=MarkdownTextObject(
                    text=f'_{self.slash.target_user} do you want to play a game? *Click* the Button ~~~~~~>_'
                ),
                accessory=ButtonElement(
                    text=f'{SHINY_WEED} {SPACE_CAT}  SPIN  {SPACE_CAT} {SHINY_WEED}',
                    value='test',
                    action_id='click_me_button'
                )
            ).to_dict(),
            DividerBlock().to_dict(),
            SectionBlock(
                text=MarkdownTextObject(
                    text=f'{"~" * 62}'
                )
            ).to_dict(),
            SectionBlock(
                text=MarkdownTextObject(
                    text=f'{WHITE_PURPLE * 10}{WHITE_DIAMOND}'
                )
            ).to_dict(),
            SectionBlock(
                text=MarkdownTextObject(
                    text=f'{WHITE_RED_PURPLE_RED * 5}{WHITE_DIAMOND}'
                )
            ).to_dict(),
            SectionBlock(
                block_id='emoji_spinner',
                text=MarkdownTextObject(
                    text=(
                        f'{PURPLE_DIAMOND} {RED_RUBY}  ~~~~  '
                        f'*| | |*   {CAT_NO_SPIN}   *| | |*   {CAT_NO_SPIN}   *| | |*   '
                        f'{CAT_NO_SPIN}   *| | |*   {CAT_NO_SPIN}   *| | |*   {CAT_NO_SPIN}   *| | |*'
                        f'  ~~~~   {RED_RUBY} {PURPLE_DIAMOND}'
                    )
                )
            ).to_dict(),
            SectionBlock(
                text=MarkdownTextObject(
                    text=f'{WHITE_RED_PURPLE_RED * 5}{WHITE_DIAMOND}'
                )
            ).to_dict(),
            SectionBlock(
                text=MarkdownTextObject(
                    text=f'{WHITE_PURPLE * 10}{WHITE_DIAMOND}'
                )
            ).to_dict(),
            SectionBlock(
                block_id='wildcard_buttons_header',
                text=MarkdownTextObject(
                    text=f'{"~" * 23} _*Dont Click These Yet!*_ {"~" * 23}'
                )
            ).to_dict(),
            ActionsBlock(
                block_id='wildcard_buttons',
                elements=[
                    ButtonElement(
                        text=f'{CHERRY_GALAXY} {SHINY_SEVEN * 3} {CHERRY_GALAXY}',
                        action_id='wildcard_button_one'
                    ),
                    ButtonElement(
                        text=f'{SHINY_WEED} {SHINY_SEVEN * 3} {SHINY_WEED}',
                        action_id='wildcard_button_two'
                    ),
                    ButtonElement(
                        text=f'{SPACE_CAT} {SHINY_SEVEN * 3} {SPACE_CAT}',
                        action_id='wildcard_button_three'
                    ),
                    ButtonElement(
                        text=f'{SHINY_WEED} {SHINY_SEVEN * 3} {SHINY_WEED}',
                        action_id='wildcard_button_four'
                    ),
                    ButtonElement(
                        text=f'{CHERRY_GALAXY} {SHINY_SEVEN * 3} {CHERRY_GALAXY}',
                        action_id='wildcard_button_five'
                    )
                ]
            ).to_dict(),
            SectionBlock(
                text=MarkdownTextObject(
                    text=f'{PARTY_UP_ARROW * 25}'
                )
            ).to_dict()
        ]
        return blocks

    def start_spinning(self) -> list:
        """Return Required Schema for All Emojis Spinning View."""
        blocks = copy.deepcopy(self.action.blocks)
        for block in blocks:
            if block['block_id'] == 'click_me_button_header':
                str_to_replace = '*Click* the Button ~~~~~~&gt;'
                orig_header_str = block['text']['text']
                new_header_str = orig_header_str.replace(
                    f'{str_to_replace}', f'<@{self.action.user_id}> clicked the button & is now playing.'
                )
                block['text']['text'] = new_header_str
                del block['accessory']

            elif block['block_id'] == 'emoji_spinner':
                orig_spinner_str = block['text']['text']
                new_spinner_str = orig_spinner_str.replace(f'{CAT_NO_SPIN}', f'{CAT_SPIN}')
                block['text']['text'] = new_spinner_str

            elif block['block_id'] == 'wildcard_buttons_header':
                block['text']['text'] = f'{"~" * 24} _*Now Click These!*_ {"~" * 25}'
                break
        return blocks

    def update_spinner_emoji(self, spinner: Spinner, emoji_to_replace: str) -> list:
        """Return Required Schema for Single Emoji Spinning View."""
        blocks = copy.deepcopy(self.action.blocks)
        new_spinner_str_to_list = copy.deepcopy(spinner.emoji_str_to_list)
        new_spinner_str_to_list[emoji_to_replace] = spinner.random_emoji
        blocks[spinner.block_index]['text']['text'] = ''.join(new_spinner_str_to_list)
        return blocks

    def loser(self, updated_blocks: list) -> list:
        """Return Required Schema for Non Winning View."""
        losing_msg = random.choice(GAME_OVER_MSGS)
        blocks = copy.deepcopy(updated_blocks)

        for i, block in enumerate(blocks):
            if block['block_id'] == 'wildcard_buttons_header':
                blocks[i]['text']['text'] = f'{"~" * 26} _*Game Over!*_ {"~" * 26}'

            elif block['block_id'] == 'wildcard_buttons':
                section_to_add = SectionBlock(
                    text=MarkdownTextObject(
                        text=(
                            f':dogelaugh:  _<@{self.action.user_id}> {losing_msg}. '
                            f'*See Ya!*_ :mario_wave:'
                        )
                    )
                ).to_dict()
                blocks[i] = section_to_add
                break
        return blocks

    def winner(self, updated_blocks: list, matches: int) -> list:
        """Return Required Schema for Non Winning View."""
        header = f'{matches} Matches'
        blocks = copy.deepcopy(updated_blocks)

        if matches == 2:
            prize = random.choice(TWO_MATCHES)
            prize_msg = f'_<@{self.action.user_id}> won *{prize["item"]}*! Check your email!_ {prize["emoji"]}'
        elif matches == 3:
            prize = random.choice(THREE_MATCHES)
            prize_msg = f'_<@{self.action.user_id}> won *{prize["item"]}*! Tag them here!_ {prize["emoji"]}'
        elif matches == 4:
            prize_msg = JACKPOT_MSG

        for i, block in enumerate(blocks):
            if block['block_id'] == 'wildcard_buttons_header':
                blocks[i]['text']['text'] = f'{"~" * 26} _*{header}!*_ {"~" * 27}'

            elif block['block_id'] == 'wildcard_buttons':
                section_to_add = SectionBlock(
                    text=MarkdownTextObject(
                        text=prize_msg
                    )
                ).to_dict()
                blocks[i] = section_to_add
                break
        return blocks

    @staticmethod
    def jackpot(updated_blocks: list) -> list:
        """Return Required Schema for Jackpot View."""
        blocks = copy.deepcopy(updated_blocks)
        for i, block in enumerate(blocks):
            if block['block_id'] == 'wildcard_buttons_header':
                blocks[i]['text']['text'] = f'{"~" *19} {MONEY_MOUTH * 3} _*JACKPOT*_ {MONEY_MOUTH * 3} {"~" * 19}'

            elif block['block_id'] == 'wildcard_buttons':
                section_to_add = SectionBlock(
                    text=MarkdownTextObject(
                        text=(
                            f'{JACKPOT_MSG}'
                        )
                    )
                ).to_dict()
                blocks[i] = section_to_add
                break
        return blocks
