from src.extract import extract_characters
from src.clean import clean_characters
from src.load import create_character_table, sync_characters


def run_pipeline():

    print("Starting pipeline...")

    characters = extract_characters()

    print(f"Extracted characters: {len(characters)}")

    cleaned_df = clean_characters(characters)

    print(f"Cleaned characters: {len(cleaned_df)}")

    create_character_table()

    sync_results = sync_characters(cleaned_df)

    print("\nPostgreSQL synchronization:")
    print(f"Inserted:   {sync_results['inserted']}")
    print(f"Updated:    {sync_results['updated']}")
    print(f"Unchanged:  {sync_results['unchanged']}")
    print(f"Deleted:    {sync_results['deleted']}")

    print("\nPipeline completed successfully.")

    return sync_results


