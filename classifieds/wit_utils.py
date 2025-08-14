import requests

WIT_TOKEN = "PXZKTJT2ZNPKIOSBGJVEZFOMK4UEBCAI"

def extract_intent_entities(message):
    url = "https://api.wit.ai/message"
    headers = {
        "Authorization": WIT_TOKEN
    }
    params = {
        "v": "20240728",
        "q": message
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
