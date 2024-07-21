import requests

API_KEY = '9c614c64bf781118ab43ebd2281d9877'
BASE_URL = 'https://api.themoviedb.org/3'

def get_content_recommendations(movie_name):
    search_url = f"{BASE_URL}/search/movie"
    search_params = {
        'api_key': API_KEY,
        'query': movie_name
    }
    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code == 200:
        search_results = search_response.json()
        if search_results['results']:
            movie_id = search_results['results'][0]['id']
            recommendations_url = f"{BASE_URL}/movie/{movie_id}/recommendations"
            recommendations_params = {
                'api_key': API_KEY
            }
            recommendations_response = requests.get(recommendations_url, params=recommendations_params)
            if recommendations_response.status_code == 200:
                recommendations_results = recommendations_response.json()
                return [movie['title'] for movie in recommendations_results['results']]
    return []
