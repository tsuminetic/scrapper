import json

def count_movies(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return len(data)
            else:
                print("Invalid JSON format. The JSON file should contain an array of movie objects.")
    except FileNotFoundError:
        print("File not found. Please provide a valid JSON file path.")
    except json.JSONDecodeError:
        print("Invalid JSON format. Please provide a valid JSON file.")

if __name__ == "__main__":
    json_file_path = "movie_data.json"
    movie_count = count_movies(json_file_path)
    if movie_count is not None:
        print(f"Number of movies in the JSON file: {movie_count}")