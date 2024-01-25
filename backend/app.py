from flask import Flask
import requests
from dotenv import load_dotenv
import os
from urllib.parse import urljoin

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
# Access environment variables
app.config['PYTHONANYWHERE_USERNAME'] = os.getenv('PYTHONANYWHERE_USERNAME')
app.config['PYTHONANYWHERE_TOKEN'] = os.getenv('PYTHONANYWHERE_TOKEN')

# NON GLOBAL
pythonanywhere_host = "eu.pythonanywhere.com"

api_base = "https://{pythonanywhere_host}/api/v0/user/{username}/".format(
    pythonanywhere_host=pythonanywhere_host,
    username=app.config['PYTHONANYWHERE_USERNAME'],
)

@app.route('/')
def hello():
    return 'Hello, Flask!'

@app.route('/list_parities')
def list_parities():
    resp = requests.get(
        urljoin(api_base, "files/path/home/{username}/".format(username=app.config['PYTHONANYWHERE_USERNAME'])),
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
)
    print(resp)
    return resp.text

@app.route('/upload_parity')
def upload_parity():
    resp = requests.post(
        urljoin(api_base, "files/path/home/{username}/foo.txt".format(username=app.config['PYTHONANYWHERE_USERNAME'])),
        files={"content": "hello world"},
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    return 'Hello, Flask!'


@app.route('/update_parity')
def update_parity():
    resp = requests.post(
        urljoin(api_base, "files/path/home/{username}/foo.txt".format(username=app.config['PYTHONANYWHERE_USERNAME'])),
        files={"content": "some new contents"},
        headers={"Authorization": "Token {api_token}".format(api_token=app.config['PYTHONANYWHERE_TOKEN'])}
    )
    return 'Hello, Flask!'

# @app.route('/cpu')
# def req_cpu():
#     response = requests.get(
#     'https://eu.pythonanywhere.com/api/v0/user/{username}/cpu/'.format(
#         username=app.config['PYTHONANYWHERE_USERNAME']
#     ),
#     headers={'Authorization': 'Token {token}'.format(token=app.config['PYTHONANYWHERE_TOKEN'])}
#     )
#     if response.status_code == 200:
#         print('CPU quota info:')
#         print(response.content)
#     else:
#         print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))
#     return f"Hello!"

if __name__ == '__main__':
    app.run(debug=True)