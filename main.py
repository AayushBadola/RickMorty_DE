from src.database_manager import (
    ensure_database_ready,
    rebuild_database,
    update_database
)

from src.query import (
    find_characters,
    get_character_by_id
)

from src.search import (
    did_you_mean,
    get_character_matches
)

from utils.display import (
    display_main_menu,
    display_developer_menu,
    get_character_name,
    display_suggestion,
    display_character_choices,
    get_character_choice,
    display_character,
    get_filter_value,
    display_filter_results,
    display_sync_results,
    pause
)


def search_character():

    name = get_character_name()

    matches = get_character_matches(name)

    if not matches:

        suggestion = did_you_mean(name)

        if suggestion is None:
            print("\nCharacter not found.")
            pause()
            return

        accepted = display_suggestion(suggestion)

        if not accepted:
            pause()
            return

        matches = get_character_matches(suggestion)

    if len(matches) == 1:

        character_id = matches[0][0]

    else:

        display_character_choices(matches)

        choice_index = get_character_choice(
            len(matches)
        )

        character_id = matches[choice_index][0]

    character = get_character_by_id(character_id)

    if character is None:
        print("\nCharacter data not found.")
    else:
        display_character(character)

    pause()


def filter_characters():

    print("\nEnter filters. Leave blank for Any.")

    status = get_filter_value("Status")
    species = get_filter_value("Species")
    gender = get_filter_value("Gender")
    origin = get_filter_value("Origin")
    location = get_filter_value("Location")

    results = find_characters(
        status=status,
        species=species,
        gender=gender,
        origin=origin,
        location=location
    )

    display_filter_results(results)

    pause()


def developer_options():

    while True:

        choice = display_developer_menu()

        if choice == 1:

            print("\nRebuilding database...")

            results = rebuild_database()

            display_sync_results(results)

            pause()

        elif choice == 2:

            print("\nChecking database for updates...")

            results = update_database()

            display_sync_results(results)

            pause()

        else:

            return


def main():

    database_initialized = ensure_database_ready()

    if database_initialized:
        print("\nDatabase initialized successfully.")

    while True:

        choice = display_main_menu()

        if choice == 1:
            search_character()

        elif choice == 2:
            filter_characters()

        elif choice == 3:
            developer_options()

        else:
            print(
                "\nThank you for using the Rick & Morty database!"
            )
            break



if __name__ == "__main__":

    main()