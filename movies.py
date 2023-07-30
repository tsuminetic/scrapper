import requests
from bs4 import BeautifulSoup
import json
import random
import string
from lxml import html
import time

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def getMovieIDs(url):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    
    movie_ids_first_scrape = set()
    movie_ids_second_scrape = set()

    movie_links = tree.xpath('//a[starts-with(@href, "/movie/watch")]')
    for link in movie_links:
        href = link.get('href')
        movie_id = href.split("-")[-1]
        movie_ids_first_scrape.add(movie_id)

    time.sleep(1)

    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    movie_links = tree.xpath('//a[starts-with(@href, "/movie/watch")]')
    for link in movie_links:
        href = link.get('href')
        movie_id = href.split("-")[-1]
        movie_ids_second_scrape.add(movie_id)

    movie_ids = list(movie_ids_first_scrape | movie_ids_second_scrape)

    return movie_ids

def getMovieInformationByID(movie_id):
    random_length = random.randint(4, 15)
    random_string = generate_random_string(random_length)
    url = "https://cineb.rs/movie/{random_string}-{movie_id}".format(random_string=random_string, movie_id=movie_id)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    genresEs = soup.find_all('a', href=lambda href: href and href.startswith('/genre/'))

    genres = []
    for x in genresEs:
        if len(genres) < 5:
            genres.append(x.get_text())
        else:
            break

    imdb_rating = 0
    try:
        imdb_rating = float(soup.select_one("button.btn-imdb").get_text().replace("IMDB: ", ""))
    except:
        print("no valid imdb rating")

    movie_data = {
        "movie_id": movie_id,
        "movie_name": soup.select_one("h2.heading-name").find("a").get_text(),
        "poster_url": soup.select_one("img.film-poster-img")["src"],
        "description": soup.select_one("div.description").get_text(),
        "genres": genres,
        "imdb_rating": imdb_rating
    }
    return movie_data

import requests
from bs4 import BeautifulSoup
import json
import random
import string
from lxml import html
import time


def main():
    base_url = "https://cineb.rs/movie"
    all_movie_details = load_existing_movie_data()

    processed_movie_ids = set(movie['movie_id'] for movie in all_movie_details)

    start_at_page = 120
    end_at_page = 650
    current_page = start_at_page

    total_pages = end_at_page - start_at_page + 1

    while current_page <= end_at_page:
        page_url = "{base_url}?page={page}".format(base_url=base_url, page=current_page)
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
        headers = {
            'User-Agent': user_agent
        }
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        movie_ids = getMovieIDs(page_url)

        for index, movie_id in enumerate(movie_ids, 1):
            if movie_id not in processed_movie_ids:
                movie_details = getMovieInformationByID(movie_id)
                all_movie_details.append(movie_details)
                processed_movie_ids.add(movie_id)

                total_movies_scraped = (current_page - start_at_page) * len(movie_ids) + index
                total_movies = total_pages * len(movie_ids)
                progress = (total_movies_scraped / total_movies) * 100

                print(f"Scraping movies - Page {current_page}/{end_at_page} - {index}/{len(movie_ids)} - Progress: {progress:.2f}%")

        with open("progress.json", "w") as progress_file:
            progress_data = {"current_page": current_page}
            json.dump(progress_data, progress_file)

        with open("movie_data.json", "w") as json_file:
            json.dump(all_movie_details, json_file, indent=2)

        current_page += 1

def load_existing_movie_data():
    try:
        with open("movie_data.json", "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []

if __name__ == "__main__":
    main()