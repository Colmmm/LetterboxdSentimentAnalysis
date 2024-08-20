import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def scrape_movie_urls(num_movies):
    # Setup WebDriver
    print("Starting to scrape movie urls!\n")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    print("Connecting to selenium service....")
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )
    print("...Connected to selenium service!")
    movie_urls = []
    page = 1
    while len(movie_urls) < num_movies:
        driver.get(f"https://letterboxd.com/films/popular/page/{page}/")
        elements = driver.find_elements(By.CSS_SELECTOR, 'a.frame')
        for element in elements:
            if len(movie_urls) >= num_movies:
                break
            movie_urls.append(element.get_attribute('href'))
        page += 1
    
    df = pd.DataFrame(movie_urls, columns=['url'])
    print("Movie urls sucessfully scraped!\nMovie urls preview:")
    print(df.head().to_string())
    print("\nClosing connection to selenium webdriver...")
    driver.quit()
    print("Connection closed sucessfully!\n\n")
    return df

def normalize_rating(star_rating):
    rating_map = {'★': 0.2, '½': 0.1}
    return sum(rating_map[char] for char in star_rating if char in rating_map)

def scrape_reviews_from_movies(movie_urls, num_reviews_per_movie):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    print("Attempting to connect to Selenium WebDriver...")
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )
    print("Successfully connected to WebDriver!")
    
    all_reviews = []

    for movie_url in movie_urls.url:
        print(f"Scraping reviews for movie: {movie_url}")
        movie_reviews = []
        page = 1
        
        try:
            driver.get(f"{movie_url}/reviews/")
            
            # Scrape movie title and release year
            try:
                movie_title_element = driver.find_element(By.CSS_SELECTOR, 'div.contextual-title h1.headline-2 a')
                movie_title = movie_title_element.text
            except NoSuchElementException:
                movie_title = None
            
            try:
                movie_year_element = driver.find_element(By.CSS_SELECTOR, 'div.contextual-title h1.headline-2 small.metadata a')
                movie_year = movie_year_element.text
            except NoSuchElementException:
                movie_year = None

            while len(movie_reviews) < num_reviews_per_movie:
                review_elements = driver.find_elements(By.CSS_SELECTOR, 'li.film-detail')
                
                for element in review_elements:
                    if len(movie_reviews) >= num_reviews_per_movie:
                        break
                    
                    review = {}
                    review['movie_title'] = movie_title
                    review['movie_year'] = movie_year

                    try:
                        # Scrape user URL
                        user_url_element = element.find_element(By.CSS_SELECTOR, 'a.avatar.-a40')
                        review['user_url'] = user_url_element.get_attribute('href')
                    except NoSuchElementException:
                        review['user_url'] = None

                    try:
                        # Scrape review text
                        review_text_element = element.find_element(By.CSS_SELECTOR, 'div.body-text.-prose.collapsible-text')
                        review['review_text'] = review_text_element.text
                    except NoSuchElementException:
                        review['review_text'] = None

                    try:
                        # Scrape rating
                        rating_element = element.find_element(By.CSS_SELECTOR, 'span.rating')
                        review['rating'] = normalize_rating(rating_element.text)
                    except NoSuchElementException:
                        review['rating'] = None

                    try:
                        # Scrape review date
                        review_date_element = element.find_element(By.CSS_SELECTOR, 'span.date > span._nobr')
                        review['review_date'] = review_date_element.text
                    except NoSuchElementException:
                        review['review_date'] = None
                    
                    review['movie_url'] = movie_url
                    
                    # Only add the review if it has text and a rating
                    if review['review_text'] and review['rating'] is not None:
                        movie_reviews.append(review)

                # Go to next page if needed
                if len(movie_reviews) < num_reviews_per_movie:
                    page += 1
                    driver.get(f"{movie_url}/reviews/page/{page}/")
                else:
                    break
            
        except TimeoutException:
            print(f"Timeout while loading reviews for movie {movie_url}")
        
        all_reviews.extend(movie_reviews)
    
    df = pd.DataFrame(all_reviews)
    print("Reviews successfully scraped from movie URLs!\nReviews preview:")
    print(df.head().to_string())
    print("\nClosing connection to selenium WebDriver...")
    driver.quit()
    print("Connection closed successfully!\n\n")
    return df




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_movies', type=int, default=100, help='Number of movie URLs to scrape')
    parser.add_argument('--num_reviews_per_movie', type=int, default=100, help='Number of movie URLs to scrape')
    args = parser.parse_args()
    
    movie_urls = scrape_movie_urls(args.num_movies)
    reviews_from_movies = scrape_reviews_from_movies(movie_urls, args.num_reviews_per_movie)
    reviews_from_movies.to_csv('/app/data/reviews_from_movies.csv', index=False)