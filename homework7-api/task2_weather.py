import requests

def get_weather():
    api_key = "c90dd2133c5e351f59399392c958abdb"
    city = input("Введите название города: ")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ru'
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']

            print(f"Температура: {temp}°C")
            print(f"Погода: {description}")
        else:
            print(f"Ошибка: {data.get('message', 'Неизвестная ошибка')}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")


if __name__ == "__main__":
    get_weather()