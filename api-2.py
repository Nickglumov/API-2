import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os


def is_shorten_link(token, url):
    api_url = "https://api.vk.com/method/utils.checkLink"
    params = {
        "v": "5.199",
        "access_token": token,
        "url": url
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        return (data.get("response", {}).get("status") == "allowed" and
                'vk.cc' in urlparse(url).netloc)
    except:
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
    return response.json()["response"]["short_url"]


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
    stats = response.json()["response"]["stats"]
    return sum(day["views"] for day in stats)


def main():
    try:
        load_dotenv()
        token = os.environ.get('VK_TOKEN')

        input_url = input("Введите ссылку: ").strip()
        if not input_url:
            raise ValueError("URL не может быть пустым")

        if is_shorten_link(token, input_url):
            clicks = count_clicks(token, input_url)
            print(f"Количество кликов: {clicks}")
        else:
            short_url = shorten_link(token, input_url)
            print(f"Сокращенная ссылка: {short_url}")

    except KeyError:
        print("Ошибка: Токен не найден")
    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    main()