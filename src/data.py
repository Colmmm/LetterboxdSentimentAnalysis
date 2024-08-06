def scrape_letterboxd_reviews(movie_url, num_reviews):
    reviews = []
    page = 1
    while len(reviews) < num_reviews:        
        response = requests.get(f"{movie_url}/reviews/page/{page}/")
        soup = BeautifulSoup(response.content, 'html.parser')
        review_elements = soup.find_all('div', class_='film-detail-content')
        
        for element in review_elements:
            if len(reviews) >= num_reviews:
                break
            
            review_text_element = element.find('div', class_='body-text -prose collapsible-text')
            review_text = review_text_element.get_text(strip=True) if review_text_element else "No review text"
            
            rating_element = element.find('span', class_='rating')
            rating = rating_element.get_text(strip=True) if rating_element else "No rating"
            
            reviews.append({'review': review_text, 'rating': rating})
        
        page += 1

    return pd.DataFrame(reviews)


if __name__ == "__main__":
    movie_url = 'https://letterboxd.com/film/some-movie'  # Replace with actual movie URL
    num_reviews = 100
    reviews_df = scrape_letterboxd_reviews(movie_url, num_reviews)
    reviews_df.to_csv('data/reviews.csv', index=False)