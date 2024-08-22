import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

def scrape_user_urls(num_users):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    print("Attempting to connect to Selenium WebDriver...")
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )
    print("...Connected to selenium service!")
    user_urls = []
    page = 1
    while len(user_urls) < num_users:
        driver.get(f"https://letterboxd.com/members/popular/this/week/page/{page}/")
        elements = driver.find_elements(By.CSS_SELECTOR, 'a.name')
        for element in elements:
            if len(user_urls) >= num_users:
                break
            user_urls.append(element.get_attribute('href'))
        page += 1
    
    df = pd.DataFrame(user_urls, columns=['url'])
    print("User urls sucessfully scraped!\nUser urls preview:")
    print(df.head().to_string())
    print("\nClosing connection to selenium webdriver...")
    driver.quit()
    print("Connection closed sucessfully!\n\n")
    return df

def normalize_rating(star_rating):
    rating_map = {'★': 0.2, '½': 0.1}
    return sum(rating_map[char] for char in star_rating if char in rating_map)

def scrape_reviews_from_users(user_urls, num_reviews_per_user):
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

    for user_url in user_urls.url:
        print(f"Scraping reviews for user: {user_url}")
        user_reviews = []
        page = 1
        while len(user_reviews) < num_reviews_per_user:
            try:
                driver.get(f"{user_url}/films/reviews/by/added/page/{page}/")
                review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.film-detail-content')
                
                for element in review_elements:
                    if len(user_reviews) >= num_reviews_per_user:
                        break
                    
                    review = {}
                    try:
                        # Scrape movie details
                        movie_name_element = element.find_element(By.CSS_SELECTOR, 'h2.headline-2 a')
                        review['movie_title'] = movie_name_element.text
                        review['movie_url'] = f"{movie_name_element.get_attribute('href')}"
                    except NoSuchElementException:
                        review['movie_title'] = None
                        review['movie_url'] = None

                    try:
                        # Scrape review
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
                        # Additional details
                        review_date_element = element.find_element(By.CSS_SELECTOR, 'span.date')
                        review['review_date'] = review_date_element.text
                    except NoSuchElementException:
                        review['review_date'] = None

                    try:
                        movie_release_date_element = element.find_element(By.CSS_SELECTOR, 'small.metadata a')
                        review['movie_year'] = movie_release_date_element.text
                    except NoSuchElementException:
                        review['movie_year'] = None

                    review['user_url'] = user_url

                    if review['review_text'] and review['rating'] is not None:
                        user_reviews.append(review)

                # Go to next page if needed
                if len(user_reviews) < num_reviews_per_user:
                    page += 1
                else:
                    break
            
            except TimeoutException:
                print(f"Timeout while loading page {page} for user {user_url}")
                break
        
        all_reviews.extend(user_reviews)
    
    df = pd.DataFrame(all_reviews)
    print("Reviews successfully scraped from user URLs!\nReviews preview:")
    print(df.head().to_string())
    print("\nClosing connection to selenium WebDriver...")
    driver.quit()
    print("Connection closed successfully!\n\n")
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_users', type=int, default=10, help='Number of user URLs to scrape')
    parser.add_argument('--num_reviews_per_user', type=int, default=10, help='Number of reviews to scrape per user')
    args = parser.parse_args()
    
    user_urls = scrape_user_urls(args.num_users)
    reviews_from_users = scrape_reviews_from_users(user_urls, args.num_reviews_per_user)
    reviews_from_users.to_csv('/app/data/reviews_from_users.csv', index=False)
