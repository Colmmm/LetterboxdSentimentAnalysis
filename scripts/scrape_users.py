import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_user_reviews(num_reviews_per_user):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )
    user_urls = []
    page = 1
    while len(user_urls) < num_reviews_per_user:
        driver.get(f"https://letterboxd.com/members/popular/this/week/page/{page}/")
        elements = driver.find_elements(By.CSS_SELECTOR, 'a.name')
        for element in elements:
            if len(user_urls) >= num_reviews_per_user:
                break
            user_urls.append(element.get_attribute('href'))
        page += 1

    reviews = []
    for user_url in user_urls:
        driver.get(f"{user_url}/films/reviews/by/added/page/1/")
        review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.film-detail-content')
        for element in review_elements:
            review_text_element = element.find_element(By.CSS_SELECTOR, 'div.body-text.-prose.collapsible-text')
            review_text = review_text_element.text if review_text_element else None
            rating_element = element.find_element(By.CSS_SELECTOR, 'span.rating')
            star_rating = rating_element.text if rating_element else None
            if review_text and star_rating is not None:
                reviews.append({'review': review_text, 'rating': star_rating})
    
    df = pd.DataFrame(reviews)
    df.to_csv('/app/data/user_reviews.csv', index=False)

scrape_user_reviews(50)  # Adjust the number as needed