import os
import sqlite3

import psycopg
from dotenv import load_dotenv

from pipeline import run_pipeline


load_dotenv()


BACKUP_DB_PATH = "data/backup_data.db"
SEARCH_DB_PATH = "data/char_names.db"


def get_postgres_connection():

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def get_sqlite_connection(db_path):

    return sqlite3.connect(db_path)


def clear_database():

    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DROP TABLE IF EXISTS characters
    """)

    connection.commit()

    cursor.close()
    connection.close()


def remove_local_snapshots():

    for database_path in [
        BACKUP_DB_PATH,
        SEARCH_DB_PATH
    ]:

        if os.path.exists(database_path):
            os.remove(database_path)


def create_backup():

    postgres_connection = get_postgres_connection()
    postgres_cursor = postgres_connection.cursor()

    postgres_cursor.execute("""
        SELECT
            id,
            name,
            status,
            species,
            type,
            gender,
            origin_name,
            location_name,
            record_hash
        FROM characters
        ORDER BY id
    """)

    characters = postgres_cursor.fetchall()

    postgres_cursor.close()
    postgres_connection.close()

    sqlite_connection = get_sqlite_connection(
        BACKUP_DB_PATH
    )
    sqlite_cursor = sqlite_connection.cursor()

    try:

        sqlite_cursor.execute("""
            DROP TABLE IF EXISTS characters
        """)

        sqlite_cursor.execute("""
            CREATE TABLE characters (
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

        sqlite_cursor.executemany("""
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, characters)

        sqlite_connection.commit()

    except Exception:

        sqlite_connection.rollback()
        raise

    finally:

        sqlite_cursor.close()
        sqlite_connection.close()


def create_search_database():

    sqlite_connection = get_sqlite_connection(
        SEARCH_DB_PATH
    )
    sqlite_cursor = sqlite_connection.cursor()

    try:

        sqlite_cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_names (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                origin_name TEXT
            )
        """)

        sqlite_connection.commit()

    except Exception:

        sqlite_connection.rollback()
        raise

    finally:

        sqlite_cursor.close()
        sqlite_connection.close()


def sync_search_index():

    postgres_connection = get_postgres_connection()
    postgres_cursor = postgres_connection.cursor()

    postgres_cursor.execute("""
        SELECT id, name, origin_name
        FROM characters
        ORDER BY id
    """)

    characters = postgres_cursor.fetchall()

    postgres_cursor.close()
    postgres_connection.close()

    create_search_database()

    sqlite_connection = get_sqlite_connection(
        SEARCH_DB_PATH
    )
    sqlite_cursor = sqlite_connection.cursor()

    try:

        sqlite_cursor.execute("""
            DELETE FROM character_names
        """)

        sqlite_cursor.executemany("""
            INSERT INTO character_names (
                id,
                name,
                origin_name
            )
            VALUES (?, ?, ?)
        """, characters)

        sqlite_connection.commit()

    except Exception:

        sqlite_connection.rollback()
        raise

    finally:

        sqlite_cursor.close()
        sqlite_connection.close()


def rebuild_database():

    clear_database()

    remove_local_snapshots()

    results = run_pipeline()

    create_backup()
    sync_search_index()

    return results


def update_database():

    results = run_pipeline()

    if (
        results["inserted"] > 0
        or results["updated"] > 0
        or results["deleted"] > 0
    ):

        create_backup()
        sync_search_index()

    return results


def database_is_ready():

    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'characters'
        )
    """)

    table_exists = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    if not table_exists:
        return False

    return (
        os.path.exists(BACKUP_DB_PATH)
        and os.path.exists(SEARCH_DB_PATH)
    )

def ensure_database_ready():

    if database_is_ready():
        return False

    rebuild_database()
    return True