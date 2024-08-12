import os
from kaggle.api.kaggle_api_extended import KaggleApi

def upload_to_kaggle():
    api = KaggleApi()
    api.authenticate()
    
    dataset_path = '/app/data/movie_reviews.csv'
    dataset_slug = 'your-username/letterboxd-movie-reviews'
    
    api.dataset_create_new(dataset_path, dataset_slug, 'Letterboxd Movie Reviews')

if __name__ == "__main__":
    upload_to_kaggle()
