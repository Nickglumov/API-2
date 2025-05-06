import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os


def is_shorten_link(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc.endswith('vk.cc') or parsed_url.netloc.endswith('vk.com')


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
    json_response = response.json()
    
    if "error" in json_response:
        raise RuntimeError(f"VK API error: {json_response['error']}")
    
    return json_response["response"]["short_url"]


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
    json_response = response.json()
    
    if "error" in json_response:
        raise RuntimeError(f"VK API error: {json_response['error']}")
    
    stats = json_response["response"]["stats"]
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

        if is_shorten_link(input_url):
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
