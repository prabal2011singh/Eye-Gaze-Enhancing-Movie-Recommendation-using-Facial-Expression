import cv2
from deepface import DeepFace
import requests

API_KEY = '9c614c64bf781118ab43ebd2281d9877'
BASE_URL = 'https://api.themoviedb.org/3'
emotion_genre_mapping = {
    'happy': ['Comedy', 'Romance', 'Family', 'Adventure', 'Animation'],
    'sad': ['Drama', 'Tragedy', 'Melodrama'],
    'surprise': ['Thriller', 'Mystery'],
    'fear': ['Horror', 'Thriller'],
    'angry': ['Action', 'Crime', 'War'],
    'disgust': ['Horror', 'Thriller', 'Crime'],
    'neutral': ['Documentary', 'Biography']
}

def predict_emotion_from_frame(frame):
    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
    if isinstance(result, list):
        result = result[0]  # Take the first detected face
    return result['dominant_emotion'].lower()

def get_genre_ids():
    url = f"{BASE_URL}/genre/movie/list"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {genre['name']: genre['id'] for genre in data['genres']}
    else:
        print("Error:", response.status_code)
        return None

def get_popular_movies(genre_id, count=5):
    url = f"{BASE_URL}/discover/movie"
    params = {
        'api_key': API_KEY,
        'with_genres': genre_id,
        'sort_by': 'vote_average.desc',
        'vote_count.gte': 100
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [movie['title'] for movie in data['results'][:count]]
    else:
        print("Error:", response.status_code)
        return None

def get_emotion_recommendations(emotion):
    genre_ids = get_genre_ids()
    recommendations = []
    if emotion in emotion_genre_mapping:
        genres = emotion_genre_mapping[emotion]
        for genre_name in genres:
            if genre_name in genre_ids:
                genre_id = genre_ids[genre_name]
                recommendations.extend(get_popular_movies(genre_id))
            else:
                print(f"Genre '{genre_name}' not found.")
    return recommendations
