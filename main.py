import models
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine, get_db
from schemas import StockRequest
from models import Stock
from utils import fetch_stock_data


app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def home(request: Request,
               name=None, forward_pe=None, dividend=None, ma50=None, ma200=None,
               db: SessionLocal = Depends(get_db)):
    """
    Display the dashboard on homepage
    :return:
    """
    stocks = db.query(Stock)

    if name:
        stocks = stocks.filter(Stock.name.startswith(name))
    if forward_pe:
        stocks = stocks.filter(Stock.forward_pe < forward_pe)
    if dividend:
        stocks = stocks.filter(Stock.dividend > dividend)
    if ma50:
        stocks = stocks.filter(Stock.price > Stock.ma50)
    if ma200:
        stocks = stocks.filter(Stock.price > Stock.ma200)
    return templates.TemplateResponse("home.html",
                                      {"request": request,
                                       "stocks": stocks,
                                       "name": name,
                                       "dividend": dividend,
                                       "forward_pe": forward_pe,
                                       "ma50": ma50,
                                       "ma200": ma200})


@app.post("/stock")
async def create_stock(stock_request: StockRequest,
                       background_tasks: BackgroundTasks,
                       db: SessionLocal = Depends(get_db)):
    """
    Create new stock entry and store it in database.
    Run background task in queue to update db entry
    with fetched stock details
    :return:
    """
    # Instantiate model with input data
    stock = Stock()
    stock.symbol = stock_request.symbol
    # Save to db
    db.add(stock)
    db.commit()

    background_tasks.add_task(fetch_stock_data, stock.id)

    return {"code": "success", "message": "Stock was added to database"}
