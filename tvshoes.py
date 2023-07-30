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

def getTVShowIDs(url):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    
    tv_show_ids_first_scrape = set()
    tv_show_ids_second_scrape = set()

    tv_show_links = tree.xpath('//a[starts-with(@href, "/tv/watch")]')
    for link in tv_show_links:
        href = link.get('href')
        tv_show_id = href.split("-")[-1]
        tv_show_ids_first_scrape.add(tv_show_id)

    time.sleep(1)

    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    tv_show_links = tree.xpath('//a[starts-with(@href, "/tv/watch")]')
    for link in tv_show_links:
        href = link.get('href')
        tv_show_id = href.split("-")[-1]
        tv_show_ids_second_scrape.add(tv_show_id)

    tv_show_ids = list(tv_show_ids_first_scrape | tv_show_ids_second_scrape)

    return tv_show_ids

def getTVShowInformationByID(tv_show_id):
    random_length = random.randint(4, 15)
    random_string = generate_random_string(random_length)
    url = "https://cineb.rs/tv/{random_string}-{tv_show_id}".format(random_string=random_string, tv_show_id=tv_show_id)
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
    tv_show_data = {
        "tv_show_id": tv_show_id,
        "tv_show_name": soup.select_one("h2.heading-name").find("a").get_text(),
        "poster_url": soup.select_one("img.film-poster-img")["src"],
        "description": soup.select_one("div.description").get_text(),
        "genres": genres,
        "imdb_rating": imdb_rating,
    }

    return tv_show_data


def main():
    base_url = "https://cineb.rs/tv-show"
    all_tv_show_details = load_existing_tv_show_data()

    processed_tv_show_ids = set(tv_show['tv_show_id'] for tv_show in all_tv_show_details)

    start_at_page = 1
    end_at_page = 350
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

        tv_show_ids = getTVShowIDs(page_url)

        for index, tv_show_id in enumerate(tv_show_ids, 1):
            if tv_show_id not in processed_tv_show_ids:
                tv_show_details = getTVShowInformationByID(tv_show_id)
                all_tv_show_details.append(tv_show_details)
                processed_tv_show_ids.add(tv_show_id)

                total_tv_shows_scraped = (current_page - start_at_page) * len(tv_show_ids) + index
                total_tv_shows = total_pages * len(tv_show_ids)
                progress = (total_tv_shows_scraped / total_tv_shows) * 100

                print(f"Scraping TV shows - Page {current_page}/{end_at_page} - {index}/{len(tv_show_ids)} - Progress: {progress:.2f}%")

        with open("tv_show_progress.json", "w") as progress_file:
            progress_data = {"current_page": current_page}
            json.dump(progress_data, progress_file)

        with open("tv_show_data.json", "w") as json_file:
            json.dump(all_tv_show_details, json_file, indent=2)

        current_page += 1

def load_existing_tv_show_data():
    try:
        with open("tv_show_data.json", "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []

if __name__ == "__main__":
    main()
