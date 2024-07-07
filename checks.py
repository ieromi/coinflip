"""
Docstring:

Модуль содержит функции для взаимодействия с блокчейном Ethereum на тестовой сети Camp.

Функции:

get_faucet_tx(address) - получает количество транзакций с фонтаном для указанного адреса.
get_bridge_tx(address) - получает количество транзакций с мостом для указанного адреса.

"""

import requests


def get_faucet_tx(address):
    """
    Получает количество транзакций с фонтаном для указанного адреса.

    Аргументы:
        address (str): Адрес блокчейна, для которого нужно проверить транзакции с фонтаном.

    Возвращает:
        int: Количество транзакций с фонтаном, если операция прошла успешно.
        Exception: Исключение, возникшее при возникновении ошибки.
    """
    try:
        faucets = 0
        uri = f'https://camp-network-testnet.blockscout.com/api/v2/addresses/{address}/internal-transactions'
        res_json = requests.get(uri).json()
        txs = res_json['items']

        for tx in txs:
            if tx['from']['hash'].lower() == "".lower():
                faucets += 1

        return faucets
    except Exception as e:
        return e


def get_bridge_tx(address):
    """
    Получает количество транзакций с мостом для указанного адреса.

    Аргументы:
        address (str): Адрес блокчейна, для которого нужно проверить транзакции с мостом.

    Возвращает:
        int: Количество транзакций с мостом, если операция прошла успешно.
        Exception: Исключение, возникшее при возникновении ошибки.
    """
    try:
        bridges = 0
        uri = f'https://camp-network-testnet.blockscout.com/api/v2/addresses/{address}/internal-transactions'
        res_json = requests.get(uri).json()
        txs = res_json['items']

        for tx in txs:
            if tx['from']['hash'].lower() == "0x4200000000000000000000000000000000000010".lower():
                bridges += 1

        return bridges
    except Exception as e:
        return e
