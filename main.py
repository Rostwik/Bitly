import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l',
        '--link',
        help='Ссылка',
        type=str,
        required=True
    )
    args = parser.parse_args()

    load_dotenv()
    bitly_token = os.getenv('BITLY_TOKEN')
    user_url = args.link

    try:
        response = requests.get(user_url)
        response.raise_for_status()

    except Exception as ex:
        print(f'К сожалению, адрес {user_url} некорректен!', ex)
        return

    if not is_bitlink(user_url, bitly_token):
        print(f'Для {user_url} еще не был создан bitlink')
        print('Ваш новый bitlink:', shorted_link(user_url, bitly_token))
        return

    print(
        'Такая короткая ссылка нашлась, кол-во кликов по ней:',
        count_clicks(user_url, bitly_token)
    )


def parsed_link(url_for_parse):
    parse_url = urlparse(url_for_parse)
    url_without_sheme = f'{parse_url.netloc}{parse_url.path}'

    return url_without_sheme


def is_bitlink(url, token):
    bitly_header = {'Authorization': f'Bearer {token}'}
    bit_url = f'https://api-ssl.bitly.com/v4/bitlinks/{parsed_link(url)}'
    response = requests.get(bit_url, headers=bitly_header)
    return response.ok


def shorted_link(url, token):
    bitly_header = {'Authorization': f'Bearer {token}'}
    bit_url = 'https://api-ssl.bitly.com/v4/bitlinks'
    bitly_body = {'long_url': url, 'title': 'Mybit'}

    response = requests.post(bit_url, headers=bitly_header, json=bitly_body)
    response.raise_for_status()

    return response.json()['id']


def count_clicks(url, token):
    bitly_params = {'unit': 'day', 'units': '-1'}
    bit_url = 'https://api-ssl.bitly.com/v4/bitlinks/' \
              f'{parsed_link(url)}/clicks/summary'

    bitly_header = {'Authorization': f'Bearer {token}'}
    response = requests.get(bit_url, headers=bitly_header, params=bitly_params)
    response.raise_for_status()

    return response.json()['total_clicks']


if __name__ == '__main__':
    main()
