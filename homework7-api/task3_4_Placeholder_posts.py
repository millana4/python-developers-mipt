import requests


def create_post_with_error_handling():
    url = "https://jsonplaceholder.typicode.com/posts"

    new_post = {
        'title': 'Заголовок',
        'body': 'Текст',
        'userId': 1
    }

    try:
        response = requests.post(url, json=new_post)

        if response.status_code == 201:
            data = response.json()
            print(f"Пост создан!")
            print(f"ID созданного поста: {data['id']}")
            print(f"Заголовок: {data['title']}")
            print(f"Содержание: {data['body']}")

        elif response.status_code == 400:
            print("Ошибка 400: Неправильный запрос")

        elif response.status_code == 404:
            print("Ошибка 404: Ресурс не найден")

        elif response.status_code == 500:
            print("Ошибка 500: Внутренняя ошибка сервера")

        else:
            print(f"Неизвестная ошибка: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения: {e}")


if __name__ == "__main__":
    create_post_with_error_handling()