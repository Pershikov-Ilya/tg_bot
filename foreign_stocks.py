import yfinance as yf

def get_foreign_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if not hist.empty:
        latest_data = hist.iloc[-1]
        return (f"Акция {ticker}:\n"
                f"Цена: {latest_data['Close']}$\n")
    else:
        return "Неверный тикер или данные недоступны."