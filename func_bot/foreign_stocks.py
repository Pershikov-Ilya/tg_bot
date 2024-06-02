import yfinance as yf

def get_foreign_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if not hist.empty:
        latest_data = hist.iloc[-1]
        return (f"{ticker}: {latest_data['Close']}$")
    else:
        return "Неверный тикер или данные недоступны."

def get_foreign_stock_data_for_info(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if not hist.empty:
        latest_data = hist.iloc[-1]
        return (f"{latest_data['Close']}$")
    else:
        return "Неверный тикер или данные недоступны."
def get_course_of_currency(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if not hist.empty:
        latest_data = hist.iloc[-1]
        return (f"{latest_data['Close']}$")
    else:
        return "Неверный тикер или данные недоступны."