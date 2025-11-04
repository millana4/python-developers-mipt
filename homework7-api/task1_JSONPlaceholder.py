import requests
import json

def get_posts():
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        posts = response.json()

        for i, post in enumerate(posts[:5], 1):
            print(f"\nID: {post['id']}")
            print(f"Заголовок: {post['title']}")
            print(f"Текст: {post['body']}")

        return posts[:5]

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка при парсинге JSON: {e}")
        return None
    except KeyError as e:
        print(f"Отсутствует ожидаемое поле в ответе: {e}")
        return None

if __name__ == "__main__":
    posts = get_posts()