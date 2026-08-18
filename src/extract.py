import os

import requests
from dotenv import load_dotenv


load_dotenv()

GRAPHQL_URL = os.getenv(
    "RICK_MORTY_GRAPHQL_URL",
    "https://rickandmortyapi.com/graphql"
)


CHARACTERS_QUERY = """
query ($page: Int!) {
    characters(page: $page) {
        info {
            count
            pages
        }

        results {
            id
            name
            status
            species
            type
            gender

            origin {
                id
                name
            }

            location {
                id
                name
            }

            image

            episode {
                id
                name
                episode
            }

            created
        }
    }
}
"""

class Character:
    def __init__(self, character_data: dict):

        self.id = character_data["id"]
        self.name = character_data["name"]
        self.status = character_data["status"]
        self.species = character_data["species"]
        self.type = character_data["type"]
        self.gender = character_data["gender"]

        self.origin_name = character_data["origin"]["name"]
        self.location_name = character_data["location"]["name"]


def extract_characters():
    """
    Extracts all character data from the Rick and Morty GraphQL API.
    """

    characters = []
    page = 1

    while True:

        response = requests.post(
            GRAPHQL_URL,
            json={
                "query": CHARACTERS_QUERY,
                "variables": {
                    "page": page
                }
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if "errors" in result:
            raise RuntimeError(result["errors"])

        character_data = result["data"]["characters"]

        characters.extend(
            Character(character)
            for character in character_data["results"]
        )

        if page >= character_data["info"]["pages"]:
            break

        page += 1

    return characters


