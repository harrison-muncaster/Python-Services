import requests
import os

from time import sleep
from typing import Optional


class PagerDuty:
    """Class representing the Pagerduty API."""
    def __init__(self, token: str) -> None:
        self.url = os.environ.get('PAGERDUTY_URL')
        self.headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Authorization': f'Token token={token}',
            'Content-Type': 'application/json'
        }

    def get(self, endpoint: str, payload: Optional[dict] = None) -> Optional[dict]:
        """Method for handling GET Requests."""
        response = requests.get(f'{self.url}/{endpoint}', headers=self.headers, params=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print('PagerDuty API Rate Limit exceeded. Sleeping 35 seconds & will retry call.')
                sleep(35)
                response = requests.get(f'{self.url}/{endpoint}', headers=self.headers, params=payload)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    response = None
                else:
                    response = response.json()
            else:
                response = None
        else:
            response = response.json()
        return response

    def get_oncall_users(self, policy_id: str, depth: int) -> Optional[list[str]]:
        """Get users currently oncall for specified PD policy & escalation level."""
        data = self.get('oncalls', {'escalation_policy_ids[]': policy_id})
        try:
            users = {
                self.get_user_by_id(user['user']['id'])['user']['email'].lower()
                for user in data['oncalls']
                if user['escalation_level'] in range(1, depth+1)
            }
        except TypeError as e:
            users = None
        return users

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user profile by specified PD ID."""
        data = self.get(f'users/{user_id}')
        return data

    def api_test(self) -> bool:
        """Verify authentication with Pagerduty & API token validity."""
        response = requests.get(f'{self.url}/users', headers=self.headers, params={'limit': 1})
        if response.status_code == 401:
            is_valid = False
        else:
            is_valid = True
        return is_valid
