from datetime import timedelta
import logging as log

from tinkoff.invest import Client, CandleInterval, InstrumentStatus
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.schemas import CandleSource
from tinkoff.invest.utils import now
from pandas import DataFrame

log.basicConfig(level=log.INFO)

def get_price(api_token, ticker):
    with Client(api_token) as cl:
        instruments: InstrumentsService = cl.instruments
        r = DataFrame(
            instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments)

        # Проверка на наличие тикера в данных
        if ticker not in r['ticker'].values:
            raise ValueError(f"Тикер {ticker} не найден.")

        figi_value = r[r['ticker'] == ticker]['figi'].iloc[0]
        log.info(f"FIGI для {ticker}: {figi_value}")

        candles_of_our_stock = []
        for candle in cl.get_all_candles(
                instrument_id=figi_value,
                from_=now() - timedelta(days=3),
                interval=CandleInterval.CANDLE_INTERVAL_5_MIN,
                candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE,
        ):
            cand = candle.close.units
            candles_of_our_stock.append(cand)

        # Проверка на пустоту списка свечей
        if not candles_of_our_stock:
            raise ValueError(f"Нет данных свечей для тикера: {ticker}")

        return candles_of_our_stock[-1]