from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime, timedelta
import pytz
import requests

app = Flask(__name__)

@app.route('/assignment2', methods=['GET'])
def get_assignment2():
    return render_template('assignment2.html')


@app.route('/assignment2', methods=['POST'])
def post_assignment2():
    days = ['','Monday',]
    symbol = request.form['symbol']
    stock = symbol.split(":")
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="
    url += stock[0]
    url += "&interval=5min&apikey=1VS6DHVM3DBWAYOH"
    r = requests.get(url)
    stock_time_series = r.json()
    if "Error Message" in stock_time_series:
        return render_template('assignment2.html', error_data="Error in API Call")
    elif "Note" in stock_time_series:
        return render_template('assignment2.html', api_call_exceeded="No. Of API Calls Exceeded for minute/day")

    url = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=" + stock[0] + "&apikey=1VS6DHVM3DBWAYOH"
    r = requests.get(url)
    stock_meta = r.json()
    stock = [stock[0], stock_meta['bestMatches'][0]["2. name"], stock_meta['bestMatches'][0]["8. currency"]]
    stock_data = {'name': stock[1], 'symbol': stock[0], 'currency': stock[2]}
    print(stock_data)
    print(stock)
    today = stock_time_series['Meta Data']['3. Last Refreshed'].split(" ")[0]
    last_day = datetime.strptime(today, '%Y-%m-%d')
    last_day -= timedelta(days=1)
    last_day = last_day.strftime('%Y-%m-%d')
    stock_data_today = stock_time_series['Time Series (Daily)'][today]
    stock_data['current'] = stock_data_today['4. close']
    stock_data['change_by_vol'] = round(float(stock_data_today['4. close']) -
                                        float(stock_time_series['Time Series (Daily)'][last_day]['4. close']),2)
    stock_data['change_by_percent'] = round((stock_data['change_by_vol']/
                                        float(stock_time_series['Time Series (Daily)'][last_day]['4. close']))*100,2)
    if stock_data['change_by_vol'] >= 0:
        stock_data['change_by_vol'] = "+" + str(stock_data['change_by_vol'])
        stock_data['change_by_percent'] = "+" + str(stock_data['change_by_percent'])
    else:
        stock_data['change_by_vol'] = str(stock_data['change_by_vol'])
        stock_data['change_by_percent'] = str(stock_data['change_by_percent'])
    pacific = datetime.now(pytz.timezone('US/Pacific'))
    temp = (pacific.strftime('%a-%b-%d-%H-%M-%S-%Y').split("-"))
    stock_data['time'] = " ".join(temp[:3])
    stock_data['time'] += " " + ":".join(temp[3:6]) + " PDT " + temp[6]
    return render_template('assignment2.html', stock_data = stock_data)




if __name__ == '__main__':
    app.run(debug=False, port=80, host='0.0.0.0')
