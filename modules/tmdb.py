import requests
import configparser

# 讀取 config.ini 檔案
config = configparser.ConfigParser()
config.read('config.ini')

# 獲取 API key
api_key = config['tmdb']['api_key']

url = "https://api.themoviedb.org/3/authentication"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(url, headers=headers)

print(response.text)