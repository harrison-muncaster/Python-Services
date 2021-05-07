import requests
import os

from typing import Optional


class Dodgeball:
    """Class representing Dodgeball API."""
    def __init__(self) -> None:
        self.url = os.environ.get('DODGEBALL_URL')

    def get(self, endpoint: str) -> Optional[dict]:
        """Method for handling GET Requests."""
        response = requests.get(f'{self.url}/{endpoint}')
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            response = None
        else:
            response = response.json()
        return response

    def get_group_members(self, group_name):
        """Get members of specified Dodgeball group."""
        data = self.get(f'group/{group_name}')
        try:
            members = {
                member['mail'].lower() for member in data['members']
                if not self.get_user(member['sAMAccountName'])['isServiceAccount']
            }
        except TypeError as e:
            members = None
        return members

    def get_user(self, username):
        """Get specific Dodgeball user profile."""
        data = self.get(f'user/{username}')
        return data
