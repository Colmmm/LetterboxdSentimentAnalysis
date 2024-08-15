import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_user_urls(num_users):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )
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
            driver.get(f"{user_url}/films/reviews/by/added/page/{page}/")
            review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.film-detail-content')
            
            for element in review_elements:
                if len(user_reviews) >= num_reviews_per_user:
                    break
                
                review_text_element = element.find_element(By.CSS_SELECTOR, 'div.body-text.-prose.collapsible-text')
                review_text = review_text_element.text if review_text_element else None
                
                rating_element = element.find_element(By.CSS_SELECTOR, 'span.rating')
                star_rating = rating_element.text if rating_element else None
                
                if review_text and star_rating is not None:
                    user_reviews.append({
                        'user_url': user_url,
                        'review': review_text,
                        'rating': normalize_rating(star_rating)
                    })
            
            # Go to next page if needed
            if len(user_reviews) < num_reviews_per_user:
                page += 1
            else:
                break
        
        all_reviews.extend(user_reviews)
    
    df = pd.DataFrame(all_reviews)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_users', type=int, default=10, help='Number of user URLs to scrape')
    parser.add_argument('--num_reviews_per_user', type=int, default=10, help='Number of reviews to scrape per user')
    args = parser.parse_args()
    
    user_urls = scrape_user_urls(args.num_users)
    reviews_from_users = scrape_reviews_from_users(user_urls, args.num_reviews_per_user)
    reviews_from_users.to_csv('/app/data/reviews_from_users.csv', index=False)
