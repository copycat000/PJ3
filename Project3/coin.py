import pyupbit
import pandas as pd
import numpy as np
from pymongo import MongoClient

URI = "mongodb+srv://copycat000:aa11bb22@cluster0.vgoizgg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(URI)
DATABASE = 'PJ3'
database = client[DATABASE]




df = pyupbit.get_ohlcv("KRW-BTC", interval = 'minute1', count = 20000)



ml = df.reset_index()
ml.rename(columns={'index':'time'},inplace = True)



ml['gap'] = ml['close'] - ml['close'].shift(1)
ml['upgap'] = np.where(ml['gap']>=0, ml['gap'], 0)
ml['downgap'] = np.where(ml['gap'] <0, ml['gap'].abs(), 0)

ml['AU'] = ml['upgap'].ewm(alpha=1/10, min_periods=10).mean()
ml['AD'] = ml['downgap'].ewm(alpha=1/10, min_periods=10).mean()

ml['RSI'] = ml['AU'] / (ml['AU'] + ml['AD']) * 100

ml['ma10'] = ml['close'].rolling(window=10).mean()
ml['stddev'] = ml['close'].rolling(window=10).std()
ml['upper'] = ml['ma10'] + 2*ml['stddev']
ml['lower'] = ml['ma10'] - 2*ml['stddev']
ml['bandwidth'] = ml['upper'] - ml['lower']

ml['disparity'] = 100*(ml['close']/ml['ma10'])

ml['up_down'] = (ml['close'] - ml['close'].shift(1)) > 0

ml['buy_sell'] = (ml['gap'].rolling(window=5).sum()) > 0

ml.drop(index=[0, 1, 2, 3, 4, 5, 6, 7, 8], axis=0, inplace = True)
ml.reset_index(inplace = True, drop = True)

db = ml.copy()
ml.drop(['time','AU','AD','upgap','downgap','upper','lower','gap','ma10','stddev','up_down'], axis = 1, inplace = True)


ml_dict = ml.to_dict('records')
coin_dict = db.to_dict('records')

collection_0 = database['bit_krw_ml']
collection_1 = database['bit_krw']

collection_0.insert_many(ml_dict)
collection_1.insert_many(coin_dict)