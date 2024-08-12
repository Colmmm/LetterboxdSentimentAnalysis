import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def scrape_reviews(num_reviews):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )
    
    movie_urls = pd.read_csv('/app/data/movie_urls.csv')['url'].tolist()
    reviews = []
    
    for movie_url in movie_urls:
        driver.get(f"{movie_url}/reviews/")
        review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.film-detail-content')
        for element in review_elements:
            if len(reviews) >= num_reviews:
                break
            review_text_element = element.find_element(By.CSS_SELECTOR, 'div.body-text.-prose.collapsible-text')
            review_text = review_text_element.text if review_text_element else None
            rating_element = element.find_element(By.CSS_SELECTOR, 'span.rating')
            star_rating = rating_element.text if rating_element else None
            if review_text and star_rating is not None:
                reviews.append({'review': review_text, 'rating': star_rating})
        if len(reviews) >= num_reviews:
            break
    
    df = pd.DataFrame(reviews)
    df.to_csv('/app/data/movie_reviews.csv', index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_reviews', type=int, default=1000, help='Number of reviews to scrape')
    args = parser.parse_args()
    
    scrape_reviews(args.num_reviews)