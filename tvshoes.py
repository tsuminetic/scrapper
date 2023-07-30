import requests
from bs4 import BeautifulSoup
import json
import random
import string
from lxml import html
import time

def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # includes uppercase letters, lowercase letters, and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def getTVShowIDs(url):
    # Define header to avoid 403 (forbidden) response
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }
    # Get HTML source code from the URL
    response = requests.get(url, headers=headers)
    # Parse HTML using lxml
    tree = html.fromstring(response.content)
    
    # Store TV show IDs in sets to avoid duplicates
    tv_show_ids_first_scrape = set()
    tv_show_ids_second_scrape = set()

    # Get all TV show links from the page - First Scrape
    tv_show_links = tree.xpath('//a[starts-with(@href, "/tv/watch")]')
    for link in tv_show_links:
        href = link.get('href')
        tv_show_id = href.split("-")[-1]
        tv_show_ids_first_scrape.add(tv_show_id)

    # Introduce a delay of 1 second before the second scraping attempt
    time.sleep(1)

    # Perform the second scraping attempt
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    # Get all TV show links from the page - Second Scrape
    tv_show_links = tree.xpath('//a[starts-with(@href, "/tv/watch")]')
    for link in tv_show_links:
        href = link.get('href')
        tv_show_id = href.split("-")[-1]
        tv_show_ids_second_scrape.add(tv_show_id)

    # Combine the two sets and convert back to a list
    tv_show_ids = list(tv_show_ids_first_scrape | tv_show_ids_second_scrape)

    return tv_show_ids

def getTVShowInformationByID(tv_show_id):
    random_length = random.randint(4, 15)
    random_string = generate_random_string(random_length)
    url = "https://cineb.rs/tv/{random_string}-{tv_show_id}".format(random_string=random_string, tv_show_id=tv_show_id)
    # Define header, so you won't get a 403 (forbidden) response
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }
    # Get HTML source code from URL
    response = requests.get(url, headers=headers)
    # Create BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")

    genresEs = soup.find_all('a', href=lambda href: href and href.startswith('/genre/'))

    # Store the first 5 genres in the genres list
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
    # Get TV show data
    tv_show_data = {
        "tv_show_id": tv_show_id,
        "tv_show_name": soup.select_one("h2.heading-name").find("a").get_text(),
        "poster_url": soup.select_one("img.film-poster-img")["src"],
        "description": soup.select_one("div.description").get_text(),
        "genres": genres,
        "imdb_rating": imdb_rating,
    }

    return tv_show_data

# Rest of the code remains the same
# ...

# Modify the main function to scrape TV shows
def main():
    # Starting URL for the first page
    base_url = "https://cineb.rs/tv-show"
    # List to store all TV show details
    all_tv_show_details = load_existing_tv_show_data()

    # Set to keep track of unique TV show IDs processed
    processed_tv_show_ids = set(tv_show['tv_show_id'] for tv_show in all_tv_show_details)

    start_at_page = 1
    end_at_page = 350
    current_page = start_at_page

    # Calculate the total number of pages to scrape
    total_pages = end_at_page - start_at_page + 1

    # Loop through all pages using pagination
    while current_page <= end_at_page:
        # Construct the URL for the current page
        page_url = "{base_url}?page={page}".format(base_url=base_url, page=current_page)
        # Get HTML source code from the URL
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
        headers = {
            'User-Agent': user_agent
        }
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Get TV show IDs from the current page
        tv_show_ids = getTVShowIDs(page_url)

        # Loop through TV show IDs and get TV show details
        for index, tv_show_id in enumerate(tv_show_ids, 1):
            # Check if the TV show ID has been processed before
            if tv_show_id not in processed_tv_show_ids:
                tv_show_details = getTVShowInformationByID(tv_show_id)
                all_tv_show_details.append(tv_show_details)
                processed_tv_show_ids.add(tv_show_id)

                # Calculate progress percentage
                total_tv_shows_scraped = (current_page - start_at_page) * len(tv_show_ids) + index
                total_tv_shows = total_pages * len(tv_show_ids)
                progress = (total_tv_shows_scraped / total_tv_shows) * 100

                # Print progress
                print(f"Scraping TV shows - Page {current_page}/{end_at_page} - {index}/{len(tv_show_ids)} - Progress: {progress:.2f}%")

        # Save the current page number to progress file
        with open("tv_show_progress.json", "w") as progress_file:
            progress_data = {"current_page": current_page}
            json.dump(progress_data, progress_file)

        # Save updated TV show details to the JSON file
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
