import json

def check_duplicates(json_data):
    seen_items = set()
    duplicates = []

    for item in json_data:
        item_hash = hash(json.dumps(item, sort_keys=True))
        if item_hash in seen_items:
            duplicates.append(item)
        else:
            seen_items.add(item_hash)

    return duplicates

if __name__ == "__main__":
    file_path = 'tv_show_data.json'

    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            duplicates = check_duplicates(json_data)

            if duplicates:
                print("Duplicates found:")
                for duplicate in duplicates:
                    print(duplicate)
            else:
                print("No duplicates found.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON data in '{file_path}'. Make sure the file contains valid JSON.")
