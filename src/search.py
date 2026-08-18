import difflib
import sqlite3

from dotenv import load_dotenv


load_dotenv()

SQLITE_DB_PATH = "data/char_names.db"


def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB_PATH)


def get_character_matches(name):

    connection = get_sqlite_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, origin_name
        FROM character_names
        WHERE LOWER(name) = LOWER(?)
        ORDER BY id
    """, (name.strip(),))

    matches = cursor.fetchall()

    cursor.close()
    connection.close()

    return matches


def get_character_names():

    connection = get_sqlite_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT name
        FROM character_names
        ORDER BY name
    """)

    names = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()
    connection.close()

    return names


def did_you_mean(name, cutoff=0.6):

    names = get_character_names()

    matches = difflib.get_close_matches(
        name.strip(),
        names,
        n=1,
        cutoff=cutoff
    )

    if matches:
        return matches[0]

    return None


