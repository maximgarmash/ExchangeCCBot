from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
import requests
import json
import constants
import re
import ReplyKeyboard

app = Flask(__name__)
sslify = SSLify(app)

URL = constants.url + constants.token


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_message(chat_id, text, reply_markup={}):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup}
    r = requests.post(url, json=answer)
    return r.json()


def parse_text(text):
    pattern = r'/\w+'
    if re.search(pattern, text):
        crypto = re.search(pattern, text).group()
        if crypto[1:] not in constants.command:
            return crypto[1:].replace('_', '-')


def get_price(crypto):
    url = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(crypto)
    r = requests.get(url).json()
    price = r[-1]['price_usd']
    return price
    # write_json(r.json(), filename='price.json')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        if message == '/start':
            send_message(chat_id, 'Добро пожаловать!\nЧем могу помочь? ...', reply_markup=ReplyKeyboard.start_markup)
        if message == '/stop':
            send_message(chat_id, 'До новых встреч!', reply_markup=ReplyKeyboard.hide_markup)
        if message == '/cryptocurrencies':
            res_coin = requests.get(constants.url_coin).json()
            send_message(chat_id, '\n'.join([coin['symbol'].ljust(15, ' ') + '/{}'.format(coin['id']).replace('-', '_') for coin in res_coin]))
        if parse_text(message):
            send_message(chat_id, get_price(parse_text(message)) + ' US$')
        return jsonify(r)
    return '<h1>ExchangeCCBot welcomes you<h1>'


def main():
    pass


if __name__ == "__main__":
    app.run()
    # main()

