from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_crypto_price(crypto_id):
    try:
        coins_list = cg.get_coins_list()
        coin_id = None
        for coin in coins_list:
            if coin['symbol'] == crypto_id or coin['id'] == crypto_id:
                coin_id = coin['id']
                break

        if not coin_id:
            return f"Не удалось найти криптовалюту с тикером {crypto_id}. Проверьте правильность тикера."

        result = cg.get_price(ids=coin_id, vs_currencies="usd")
        if coin_id in result and 'usd' in result[coin_id]:
            price = result[coin_id]['usd']
            return f"{crypto_id}: {price}$"
        else:
            return f"Не удалось получить данные для {crypto_id}. Проверьте правильность тикера."
    except Exception as e:
        return f"Произошла ошибка при получении данных: {e}"