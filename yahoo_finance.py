import yfinance as yf


def get_asia_and_indonesia_stock_exchange_info():
    market = yf.Market("ASIA")
    asia_market_data = market.summary
    ihsg = yf.Ticker("^JKSE")
    ihsg_data = ihsg.info
    return asia_market_data, ihsg_data
