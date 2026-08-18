import hashlib

import pandas as pd


def characters_to_dataframe(characters):

    rows = []

    for character in characters:

        rows.append({
            "id": character.id,
            "name": character.name,
            "status": character.status,
            "species": character.species,
            "type": character.type,
            "gender": character.gender,
            "origin_name": character.origin_name,
            "location_name": character.location_name
        })

    return pd.DataFrame(rows)


def handle_missing_values(df):

    text_columns = [
        "status",
        "species",
        "type",
        "gender",
        "origin_name",
        "location_name"
    ]

    df[text_columns] = df[text_columns].fillna("Unknown")

    return df


def normalize_character_data(df):

    text_columns = [
        "name",
        "status",
        "species",
        "type",
        "gender",
        "origin_name",
        "location_name"
    ]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    return df


def generate_record_hash(row):

    values = [
        row["id"],
        row["name"],
        row["status"],
        row["species"],
        row["type"],
        row["gender"],
        row["origin_name"],
        row["location_name"]
    ]

    record = "|".join(str(value) for value in values)

    return hashlib.sha256(
        record.encode("utf-8")
    ).hexdigest()


def add_record_hash(df):

    df["record_hash"] = df.apply(
        generate_record_hash,
        axis=1
    )

    return df


def validate_character_data(df):

    required_columns = {
        "id",
        "name",
        "status",
        "species",
        "type",
        "gender",
        "origin_name",
        "location_name",
        "record_hash"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df["id"].isna().any():
        raise ValueError("Character IDs cannot be missing.")

    if df["name"].isna().any():
        raise ValueError("Character names cannot be missing.")

    if df["id"].duplicated().any():
        raise ValueError("Duplicate character IDs detected.")

    if df["record_hash"].isna().any():
        raise ValueError("Record hashes cannot be missing.")

    return True


def clean_characters(characters):

    df = characters_to_dataframe(characters)

    df = handle_missing_values(df)

    df = normalize_character_data(df)

    df = add_record_hash(df)

    validate_character_data(df)

    return df


