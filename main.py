from urllib.parse import urlparse
import os
import argparse

import requests
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'link',
        help='The script works with Bitly links, the "-l" parameter is a link, it is required',
        type=str,
    )
    args = parser.parse_args()

    load_dotenv()
    bitly_token = os.getenv('BITLY_TOKEN')
    user_url = args.link

    try:
        response = requests.get(user_url)
        response.raise_for_status()

    except requests.exceptions.HTTPError:
        print(f'К сожалению, адрес {user_url} некорректен!')
        return

    if not is_bitlink(user_url, bitly_token):
        print(f'Для {user_url} еще не был создан bitlink')
        print('Ваш новый bitlink:', get_shorted_link(user_url, bitly_token))
        return

    print(
        'Такая короткая ссылка нашлась, кол-во кликов по ней:',
        get_count_clicks(user_url, bitly_token)
    )


def get_parsed_link(url_for_parse):
    parse_url = urlparse(url_for_parse)
    url_without_sheme = f'{parse_url.netloc}{parse_url.path}'

    return url_without_sheme


def is_bitlink(url, token):
    bitly_header = {'Authorization': f'Bearer {token}'}
    bit_url = f'https://api-ssl.bitly.com/v4/bitlinks/{get_parsed_link(url)}'
    response = requests.get(bit_url, headers=bitly_header)
    return response.ok


def get_shorted_link(url, token):
    bitly_header = {'Authorization': f'Bearer {token}'}
    bit_url = 'https://api-ssl.bitly.com/v4/bitlinks'
    bitly_body = {'long_url': url, 'title': 'Mybit'}

    response = requests.post(bit_url, headers=bitly_header, json=bitly_body)
    response.raise_for_status()

    return response.json()['id']


def get_count_clicks(url, token):
    bitly_params = {'unit': 'day', 'units': '-1'}
    bit_url = 'https://api-ssl.bitly.com/v4/bitlinks/' \
              f'{get_parsed_link(url)}/clicks/summary'

    bitly_header = {'Authorization': f'Bearer {token}'}
    response = requests.get(bit_url, headers=bitly_header, params=bitly_params)
    response.raise_for_status()

    return response.json()['total_clicks']


if __name__ == '__main__':
    main()
