import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os


def is_shorten_link(token, url):
    parsed_url = urlparse(url)
    if not parsed_url.netloc.endswith('vk.cc'):
        return False
    
    try:
        api_url = "https://api.vk.com/method/utils.checkLink"
        params = {
            "v": "5.199",
            "access_token": token,
            "url": url
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        response_data = response.json()
        
        if "error" in response_data:
            return False
            
        return response_data.get("response", {}).get("status") == "ok"
    except requests.exceptions.RequestException:
        return False

def shorten_link(token, long_url):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    params = {
        "v": "5.199",
        "access_token": token,
        "url": long_url,
        "private": 0
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    response_data = response.json()
    
    if "error" in response_data:
        raise RuntimeError(f"VK API error: {response_data['error']}")
    
    return response_data["response"]["short_url"]


def count_clicks(token, short_url):
    api_url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "v": "5.199",
        "access_token": token,
        "key": short_url.replace("https://vk.cc/", ""),
        "interval": "day"
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    response_data = response.json()
    
    if "error" in response_data:
        raise RuntimeError(f"VK API error: {response_data['error']}")
    
    stats = response_data["response"]["stats"]
    return sum(day["views"] for day in stats)


def main():
    load_dotenv()
    try:
        token = os.environ['VK_TOKEN']
    except KeyError as e:
        raise ValueError("Переменная окружения VK_TOKEN не найдена.") from e
    
    try:
        input_url = input("Введите ссылку: ").strip()
        if not input_url:
            raise ValueError("URL не может быть пустым")

        if is_shorten_link(token, input_url):
            clicks = count_clicks(token, input_url)
            print(f"Количество кликов: {clicks}")
        else:
            short_url = shorten_link(token, input_url)
            print(f"Сокращенная ссылка: {short_url}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении HTTP запроса: {str(e)}")
    except ValueError as e:
        print(f"Ошибка ввода: {str(e)}")
    except RuntimeError as e:
        print(f"Ошибка VK API: {str(e)}")


if __name__ == "__main__":
    main()
