from collections import Counter
import copy
from functools import cached_property
import random
import re

from bf_rig import settings


EMOJIS = settings.get('emojis')
CAT_SPIN = EMOJIS['cat_spin']
RED_RUBY = EMOJIS['red_ruby']
PURPLE_DIAMOND = EMOJIS['purple_diamond']
EMOJI_SPINNER_BLOCK_ID = 'emoji_spinner'
SPINNER_EMOJIS = settings.get('spinner_emojis')


class Spinner:
    """Class Representing the Spinner."""
    def __init__(self, blocks: list) -> None:
        self.blocks = list(blocks)

    @property
    def is_spinning(self) -> str:
        return CAT_SPIN

    @property
    def player_id(self) -> str:
        for block in self.blocks:
            if block['block_id'] == 'click_me_button_header':
                header_str_to_list = block['text']['text'].split()
                user_id = [x for x in header_str_to_list if re.search('^<@.*>$', x)]
                return user_id[0].split('<@')[-1].split('>')[0]

    @cached_property
    def random_emoji(self) -> str:
        return random.choice(SPINNER_EMOJIS)

    @cached_property
    def block_index(self) -> int:
        for i, block in enumerate(self.blocks):
            if block['block_id'] == EMOJI_SPINNER_BLOCK_ID:
                return i

    @cached_property
    def emoji_str_to_list(self) -> list:
        return re.split(r'(\s+)', self.blocks[self.block_index]['text']['text'])

    @cached_property
    def all_emojis(self) -> list:
        return [
            emoji for emoji in self.emoji_str_to_list
            if re.search('^:.*:$', emoji)
            and emoji != RED_RUBY
            and emoji != PURPLE_DIAMOND
        ]

    @cached_property
    def final_emojis(self) -> list:
        emojis = copy.deepcopy(self.all_emojis)
        for i, emoji in enumerate(emojis):
            if emoji == self.is_spinning:
                emojis[i] = self.random_emoji
                break
        return emojis

    @cached_property
    def win_count(self) -> int:
        return Counter(self.final_emojis).most_common()[0][1]

    @cached_property
    def emoji_positions(self) -> list:
        return [
            i for i, emoji in enumerate(self.emoji_str_to_list)
            if emoji in self.all_emojis
        ]

    @cached_property
    def is_on_last_spin(self) -> bool:
        return True if self.all_emojis.count(self.is_spinning) == 1 else False

    @property
    def emoji_one(self) -> str:
        return self.all_emojis[0]

    @property
    def emoji_two(self) -> str:
        return self.all_emojis[1]

    @property
    def emoji_three(self) -> str:
        return self.all_emojis[2]

    @property
    def emoji_four(self) -> str:
        return self.all_emojis[3]

    @property
    def emoji_five(self) -> str:
        return self.all_emojis[4]
