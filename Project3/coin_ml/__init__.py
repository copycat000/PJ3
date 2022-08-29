from flask import Flask, render_template, request
import jwt
import os
import time
from pymongo import MongoClient
import pandas as pd
import pickle
import lightgbm
from sklearn.metrics import roc_curve, roc_auc_score, f1_score, accuracy_score, recall_score, precision_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV

def create_app():

    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Hello Flask!'


    @app.route('/dashboard')
    def dashboard():
        METABASE_SITE_URL = "http://127.0.0.1:3000"
        METABASE_SECRET_KEY = "5dd42adf14eb50ba791816e4a7c9b65164016b5e3a738324bdbeb94fafeca3b2"

        payload = {
            "resource": {"dashboard": 4},
            "params": {},
            "exp": round(time.time()) + (60 * 10) # 10 minute expiration
            }
        token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
        iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"

        html = render_template('index.html', iframeUrl=iframeUrl)

        return html, 200

    @app.route('/model')
    def model():
        return render_template('buysell.html')


    @app.route('/predict', methods=['POST'])
    def make_prediction():
        if request.method =='POST':

            URI = "mongodb+srv://copycat000:aa11bb22@cluster0.vgoizgg.mongodb.net/?retryWrites=true&w=majority"
            client = MongoClient(URI)
            database = client['PJ3']
            bit_ml = database['bit_krw_ml']
            a = []

            for i in bit_ml.find():
                a.append(i)        

            b = pd.DataFrame(a)
            b.drop(['_id','buy_sell'], axis = 1, inplace = True)

            c = b.iloc[19897:,:]

            price = c['open'].mean()
            high = c['high'].mean()
            low = c['low'].mean()
            close = c['close'].mean()
            value = c['value'].mean()

            volume = request.form['volume']
            rsi = request.form['rsi']
            bandwidth = request.form['bandwidth']
            disparity = request.form['disparity']


            params = [price, high, low, close, volume, value, rsi, bandwidth, disparity]
            df = pd.DataFrame(params).T
            df.columns = ['open', 'high', 'low', 'close', 'volume', 'value', 'RSI', 'bandwidth', 'disparity'] 

            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            df['value'] = pd.to_numeric(df['value'])
            df['RSI'] = pd.to_numeric(df['RSI'])
            df['bandwidth'] = pd.to_numeric(df['bandwidth'])
            df['disparity'] = pd.to_numeric(df['disparity'])

            with open('coin_ml/model.pkl', 'rb') as pf:
                model = pickle.load(pf)


            y_pred = model.predict(df)

            zzz = None

            if y_pred[0] == True:
                zzz = '매수'

            elif y_pred[0] == False:
                zzz = '매도'
            
            else :
                zzz = '미정값'

            return render_template('buysell.html', predict=zzz)
    return app
##############################################################################
     

         
    

    



        

