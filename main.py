import sqlite3
import requests
import json
from flask import Flask

DB_NAME = 'db.sqlite3'
TABLE_NAME = 'api_post'
app = Flask(__name__)

connection = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = connection.cursor()

userdata = {
    "username": "admin",
    "password": "admin",
    "email": "admin@example.com"
}
token_create_endpoint = "https://test-blog-api-vmxh.onrender.com/auth/token/login/"
post_list_endpoint = "https://test-blog-api-vmxh.onrender.com/posts/"


def get_access_token():
    """
    Возвращает токен
    для аутентификации в системе.
    """
    data = {
        "username": userdata["username"],
        "password": userdata["password"]
    }
    # Преобразуем объект Response в словарь Python
    # и получаем значение ключа auth_token
    response = requests.post(token_create_endpoint, data=data).json()
    return response['auth_token']


@app.route('/')
def get_all_posts():
    """
    Возвращает все опубликованные посты
    """

    access_token = get_access_token()
    headers = {"Authorization": f"token {access_token}",
               "Accept": "application/json"
               }
    response = requests.get(post_list_endpoint,
                            headers=headers)
    statement = f"INSERT INTO {TABLE_NAME}(title, body, owner) values(?, ?, ?)"

    try:
        for el in response.json():
            cursor.execute(statement,
                           (el['title'], el['description'], el['author']))
            connection.commit()

        response = app.response_class(
            response=json.dumps({'STATUS': 'OK'}),
            status=200,
            mimetype='application/json'
        )
        return response
    except json.JSONDecodeError as e:
        print(f'Error: {e}')
        return f'Некорректный ответ от сервера'


if __name__ == '__main__':
    app.run(debug=True)
