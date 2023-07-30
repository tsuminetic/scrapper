import json

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON data in '{file_path}'. Make sure the file contains valid JSON.")
    return None

def find_similar_items(json_data1, json_data2):
    similar_items = []

    for item1 in json_data1:
        for item2 in json_data2:
            if item1 == item2:
                similar_items.append(item1)
                break

    return similar_items

def remove_items_from_json(json_data, items_to_remove):
    for item in items_to_remove:
        if item in json_data:
            json_data.remove(item)

if __name__ == "__main__":
    file1_path = 'tv_show_data.json'
    file2_path = 'search_data.json'

    json_data1 = load_json(file1_path)
    json_data2 = load_json(file2_path)

    if json_data1 and json_data2:
        similar_items = find_similar_items(json_data1, json_data2)

        if similar_items:
            print("Similar items found:")
            for item in similar_items:
                print(item)

            remove_items_from_json(json_data2, similar_items)

            try:
                with open(file2_path, 'w') as file:
                    json.dump(json_data2, file, indent=4)
                print("Similar items removed from the second file.")
            except Exception as e:
                print(f"Error saving modified data to '{file2_path}': {e}")
        else:
            print("No similar items found.")
