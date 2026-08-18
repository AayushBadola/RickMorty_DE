def print_title(title):
    print("\n" + "=" * 50)
    print(f"{title:^50}")
    print("=" * 50)


def pause():
    input("\nPress Enter to continue...")


def display_main_menu():
    print_title("Rick & Morty Database")

    print("1. Search Character")
    print("2. Find Characters")
    print("3. Developer Options")
    print("4. Exit")

    return get_valid_choice(1, 4)


def display_developer_menu():
    print_title("Developer Options")

    print("1. Rebuild Database")
    print("2. Update Database")
    print("3. Back")

    return get_valid_choice(1, 3)


def get_valid_choice(minimum, maximum):

    while True:

        choice = input(
            f"\nEnter Choice ({minimum}-{maximum}): "
        ).strip()

        if choice.isdigit():

            choice = int(choice)

            if minimum <= choice <= maximum:
                return choice

        print(
            f"Please enter a valid choice "
            f"({minimum}-{maximum})."
        )


def get_character_name():
    return input("\nEnter Character Name: ").strip()


def display_suggestion(suggestion):
    print(f"\nDid you mean {suggestion}?")

    while True:

        choice = input("Y/N: ").strip().upper()

        if choice == "Y":
            return True

        if choice == "N":
            return False

        print("Please enter Y or N.")


def display_character_choices(matches):

    print_title("Multiple Characters Found")

    for index, match in enumerate(matches, start=1):

        character_id, name, origin_name = match

        print(f"{index}. {name}")
        print(f"   Origin: {origin_name}")


def get_character_choice(match_count):

    return get_valid_choice(1, match_count) - 1


def display_character(character):

    print_title(character["name"])

    print(f"ID              : {character['id']}")
    print(f"Status          : {character['status']}")
    print(f"Species         : {character['species']}")
    print(f"Type            : {character['type']}")
    print(f"Gender          : {character['gender']}")
    print(f"Origin          : {character['origin_name']}")
    print(f"Location        : {character['location_name']}")


def get_filter_value(label):

    value = input(
        f"{label} (press Enter for any): "
    ).strip()

    if value == "":
        return None

    return value


def display_filter_results(results):

    if not results:
        print("\nNo characters found.")
        return

    print_title(
        f"Characters Found: {len(results)}"
    )

    for character in results:

        print(f"ID       : {character[0]}")
        print(f"Name     : {character[1]}")
        print(f"Status   : {character[2]}")
        print(f"Species  : {character[3]}")
        print(f"Type     : {character[4]}")
        print(f"Gender   : {character[5]}")
        print(f"Origin   : {character[6]}")
        print(f"Location : {character[7]}")
        print("-" * 50)


def display_sync_results(results):

    print_title("Database Synchronization")

    print(f"Inserted   : {results['inserted']}")
    print(f"Updated    : {results['updated']}")
    print(f"Unchanged  : {results['unchanged']}")
    print(f"Deleted    : {results['deleted']}")

    if (
        results["inserted"] == 0
        and results["updated"] == 0
        and results["deleted"] == 0
    ):
        print("\nDatabase is already up to date.")
    else:
        print("\nDatabase updated successfully.")