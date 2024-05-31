from datetime import timedelta

from tinkoff.invest import Client, CandleInterval, InstrumentStatus
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.schemas import CandleSource
from tinkoff.invest.utils import now
from pandas import DataFrame


def get_price(api_token, ticker):
    with Client(api_token) as cl:
        instruments: InstrumentsService = cl.instruments
        r = DataFrame(
            instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments)
        r = r[r['ticker'] == ticker]['figi'].iloc[0]
        figi_value = r

        candles_of_our_stock = []
        for candle in cl.get_all_candles(
                instrument_id=figi_value,
                from_=now() - timedelta(days=1),
                interval=CandleInterval.CANDLE_INTERVAL_5_MIN,
                candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE,
        ):
            cand = candle.close.units
            candles_of_our_stock.append(cand)
        return candles_of_our_stock[-1]