import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_postgres_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def find_characters(
    status=None,
    species=None,
    gender=None,
    origin=None,
    location=None
):
    conditions = []
    parameters = []

    if status is not None:
        conditions.append("status = %s")
        parameters.append(status)

    if species is not None:
        conditions.append("species = %s")
        parameters.append(species)

    if gender is not None:
        conditions.append("gender = %s")
        parameters.append(gender)

    if origin is not None:
        conditions.append("origin_name = %s")
        parameters.append(origin)

    if location is not None:
        conditions.append("location_name = %s")
        parameters.append(location)

    query = """
        SELECT
            id,
            name,
            status,
            species,
            type,
            gender,
            origin_name,
            location_name
        FROM characters
    """

    if conditions:
        query += "\nWHERE " + "\nAND ".join(conditions)

    query += "\nORDER BY id"

    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute(query, parameters)

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


if __name__ == "__main__":

    print("\nAlive characters:")
    results = find_characters(status="Alive")
    print(f"Found: {len(results)}")

    print("\nAlive Humans:")
    results = find_characters(
        status="Alive",
        species="Human"
    )
    print(f"Found: {len(results)}")

    print("\nDead Humans from Earth (C-137):")
    results = find_characters(
        status="Dead",
        species="Human",
        origin="Earth (C-137)"
    )
    print(f"Found: {len(results)}")


def get_character_by_id(character_id):

    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            status,
            species,
            type,
            gender,
            origin_name,
            location_name
        FROM characters
        WHERE id = %s
    """, (character_id,))

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "status": row[2],
        "species": row[3],
        "type": row[4],
        "gender": row[5],
        "origin_name": row[6],
        "location_name": row[7]
    }