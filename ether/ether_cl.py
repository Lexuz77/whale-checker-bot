from etherscan import Etherscan
import requests
import json


eth = Etherscan('2BW27IVCDHM38PE4QFJN3PE5KMTCDP4BG4') # Use your API key here!


subscriptions = {} # Set up a dictionary which keeps a track of what users are subscribing to


def transactions(wallet: str) -> list:
    '''Receive new transactions linked to the wallet'''
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 10,
        'sort': 'asc',
        'apikey': '2BW27IVCDHM38PE4QFJN3PE5KMTCDP4BG4' # Use your API key here!
    }
    
    response = requests.get('https://api.etherscan.io/api', params=url_params)
    response_parsed = json.loads(response.content)
    if response_parsed['message'] == 'OK':
        txs = response_parsed['result']
        return [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} \
                for tx in txs ]


def update_subscriptions(chat_id, wallet):
    '''Update the "subscriptions" dictionary'''
    global subscriptions
    txs = transactions(wallet)
    if chat_id not in subscriptions.keys():
        subscriptions[chat_id] = {}
    subscriptions[chat_id][wallet] = get_latest_tx(txs)


def get_wallet_balance(wallet):
    '''Get the amount of ETH in the wallet and the dollar amounts'''
    return f'ETH count: {format(float(eth.get_eth_balance(address=wallet)) / 1000000000000000000, "#>10,.2f")}\n'\
           f'USD: {format((float(eth.get_eth_balance(address=wallet)) / 1000000000000000000) * float(eth.get_eth_last_price()["ethusd"]), "#>10,.2f")}'


def get_balance_with_token(wallet, token_address):
    '''Get the number of tokens by token contract address'''
    return f'Token count: {format(float(eth.get_acc_balance_by_token_and_contract_address(address=wallet, contract_address=token_address)) / 1000000, "#>10,.2f")}'


def get_latest_tx(txs: list) -> int:
    '''Get the latest transaction from a list of transactions, based on timestamp'''
    return max(txs,key=lambda tx: int(tx['timestamp']))


def format_tx(tx: dict) -> str:
    '''Format a transaction dict item to printable string'''
    return f'From: {tx["from"]}, To: {tx["to"]}, Amount: {tx["value"]}'


#print(get_balance_with_token('0x0716a17fbaee714f1e6ab0f9d59edbc5f09815c0', '0x16756EC1DEb89A2106C35E0B586a799D0A61837D'))
#print(float(eth.get_eth_last_price()['ethusd']))
#print(get_wallet_balance('0x0716a17fbaee714f1e6ab0f9d59edbc5f09815c0'))


#print(type(transactions('0xDBF5E9c5206d0dB70a90108bf936DA60221dC080')))