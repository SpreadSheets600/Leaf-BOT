import json
from coinpaprika.client import Client

client = Client()
coins = client.coins()

coin_data_dict = {}

for coin in coins:
    id = coin['id']
    name = coin['name']
    symbol = coin['symbol']
    active = coin['is_active']
    type = coin['type']

    if not active:
        continue

    elif type != 'coin':
        continue

    coin_data_dict[symbol] = {
        'id': id,
        'name': name
    }

with open('Currency.json', 'w') as file:
    json.dump(coin_data_dict, file, indent=4)

print(f'DONE! {len(coin_data_dict)} Coins Added')
