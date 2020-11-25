from database import SessionLocal
from models import Stock
import yfinance as yf


def fetch_stock_data(stock_id: int):
    db = SessionLocal()
    stock = db.query(Stock).filter(Stock.id == stock_id).first()

    yahoo_data = yf.Ticker(stock.symbol)
    print(yahoo_data.info)
    stock.name = yahoo_data.info['longName']
    stock.ma200 = yahoo_data.info['twoHundredDayAverage']
    stock.ma50 = yahoo_data.info['fiftyDayAverage']
    stock.price = yahoo_data.info['previousClose']
    stock.forward_pe = yahoo_data.info['forwardPE']
    stock.forward_eps = yahoo_data.info['forwardEps']
    if yahoo_data.info['dividendYield'] is not None:
        stock.dividend = yahoo_data.info['dividendYield'] * 100
    else:
        stock.dividend = 0

    db.add(stock)
    db.commit()
