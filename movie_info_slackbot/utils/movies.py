import logging
import os

import requests
import yaml
from slack_sdk.models.blocks import Option

logging.basicConfig(level=logging.ERROR)


class MovieDatabaseAPI:
    """Class Representing the Movie Database API."""
    def __init__(self):
        self.base_url = os.environ.get('MOVIE_DATABASE_URL_DEMO')
        self.token = os.environ.get('MOVIE_DATABASE_TOKEN_DEMO')
        self.headers = {
            'Authorization': f'Bearer {self.token}'
        }

    def get_movie_by_id(self, movie_id: str) -> dict:
        """Return Movie Info by Specified Movie ID."""
        try:
            resp = requests.get(f'{self.base_url}/movie/{movie_id}', headers=self.headers)
            resp.raise_for_status()
        except Exception as e:
            logging.error(e)
            raise
        else:
            return resp.json()

    def filter_movies_by_title(self, movie_title: str) -> list:
        """Return List of Movies Filtered by Movie Title."""
        try:
            with open('movies.yml', 'r') as movies_file:
                movies_list = yaml.safe_load(movies_file)['movies']
        except Exception as e:
            logging.error(e)
            raise
        else:
            options = [
                Option(
                    text=movie['title'],
                    value=movie['id']
                )
                for movie in movies_list
                if movie_title.lower() in movie['title'].lower()
            ]
            return options
