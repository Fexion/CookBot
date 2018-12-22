import requests
from googleapiclient.discovery import build

def detect_food_request(text, key):
    endpoint = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/food/detect"
    params = {"text": text}
    headers = {
        "X-Mashape-Key": key,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    return requests.post(endpoint, params=params, headers=headers)


def search_recipe(dish, ingredients, key):
    endpoint = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/searchComplex'
    params = {
        'includeIngredients': ','.join(ingredients),
        'query': dish,
        'limitLicense': False,
        'number': 100,
        'offset': 0,
        'addRecipeInformation': True,
        'fillIngredients': True,
        'instructionsRequired': True,
    }
    headers = {
        "X-Mashape-Key": key,
        "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com"
    }

    return requests.get(endpoint, params=params, headers=headers)


def get_random_recipe(num=100, tags="", key=None):
    endpoint = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com\
            /recipes/random"
    params = {
        "number": num,
        "tags": tags
    }
    headers = {
        "X-Mashape-Key": key,
        "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com"
    }
    return requests.get(endpoint, params=params, headers=headers)


#def get_video_link(name, key):
#    return 'https://www.youtube.com/embed/ggOcObAP3lA'


# def get_video_link(query, key, maxLength = 999, minLength = 0, number = 10):
#     headers = {
#         "X-Mashape-Key": key,
#         "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com"
#     }

#     endpoint = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/food/videos/search"

#     params = {
#         "query": query,
#     }

#     prober = requests.get(endpoint, params = params, headers = headers).json()
#     if not prober['totalResults']:
#         return 'No videos found'
#     return "https://www.youtube.com/embed/" + prober['videos'][0]['youTubeId']


def get_video_link(search_term, key):

    api_key = key
    cse_id = "011956017813946754500:ua4ufdjsuds"
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term + " recipe", cx=cse_id, siteSearch="youtube.com").execute()
    return res['items'][0]['link'].replace("/watch?v=", "/embed/")
