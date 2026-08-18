import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def create_character_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT,
            species TEXT,
            type TEXT,
            gender TEXT,
            origin_name TEXT,
            location_name TEXT,
            record_hash TEXT NOT NULL
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()


def get_existing_hashes(cursor):

    cursor.execute("""
        SELECT id, record_hash
        FROM characters
    """)

    return dict(cursor.fetchall())


def insert_character(cursor, character):

    cursor.execute("""
        INSERT INTO characters (
            id,
            name,
            status,
            species,
            type,
            gender,
            origin_name,
            location_name,
            record_hash
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        int(character["id"]),
        character["name"],
        character["status"],
        character["species"],
        character["type"],
        character["gender"],
        character["origin_name"],
        character["location_name"],
        character["record_hash"]
    ))


def update_character(cursor, character):

    cursor.execute("""
        UPDATE characters
        SET
            name = %s,
            status = %s,
            species = %s,
            type = %s,
            gender = %s,
            origin_name = %s,
            location_name = %s,
            record_hash = %s
        WHERE id = %s
    """, (
        character["name"],
        character["status"],
        character["species"],
        character["type"],
        character["gender"],
        character["origin_name"],
        character["location_name"],
        character["record_hash"],
        int(character["id"])
    ))


def delete_character(cursor, character_id):

    cursor.execute("""
        DELETE FROM characters
        WHERE id = %s
    """, (character_id,))


def sync_characters(df):

    connection = get_connection()
    cursor = connection.cursor()

    existing_hashes = get_existing_hashes(cursor)

    api_ids = set()
    inserted = 0
    updated = 0
    unchanged = 0
    deleted = 0

    for _, character in df.iterrows():

        character_id = int(character["id"])
        record_hash = character["record_hash"]

        api_ids.add(character_id)

        if character_id not in existing_hashes:

            insert_character(cursor, character)
            inserted += 1

        elif existing_hashes[character_id] == record_hash:

            unchanged += 1

        else:

            update_character(cursor, character)
            updated += 1

    database_ids = set(existing_hashes.keys())

    deleted_ids = database_ids - api_ids

    for character_id in deleted_ids:

        delete_character(cursor, character_id)
        deleted += 1

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "deleted": deleted
    }


