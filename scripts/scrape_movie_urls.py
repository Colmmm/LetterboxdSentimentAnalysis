import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def scrape_movie_urls(num_movies):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        options=options
    )
    
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
    df.to_csv('/app/data/movie_urls.csv', index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_movies', type=int, default=100, help='Number of movie URLs to scrape')
    args = parser.parse_args()
    
    scrape_movie_urls(args.num_movies)
