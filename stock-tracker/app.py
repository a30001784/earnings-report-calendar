#!/usr/bin/env python
# functions to get and parse data from FinViz
from bs4 import BeautifulSoup as bs
import requests
import time
from requests_html import HTMLSession
import pandas as pd
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import sys
from pandas_datareader import data as pdr
import yfinance as yf
from datetime import datetime, timedelta, date
import numpy as np
import configparser
import os

CONFIG_FILE = './config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
start = datetime.now() - timedelta(days=10)
start.strftime('%Y-%m-%d')
end = datetime.today().strftime('%Y-%m-%d')
qq_password = os.getenv("QQ_PASSWORD")   # Assuming the password is stored in an environment variable
timestr = time.strftime("%Y-%m-%d")
finantial_ratio_file_name = "finantial_ratio_" + timestr + ".csv"
namelist = ['it']


metric = ['P/B',
'P/E',
# 'Forward P/E',
# 'PEG',
#'Debt/Eq',
'EPS (ttm)',
#'Dividend %',
'ROE',
'EPS Q/Q',
'Insider Own',
'Inst Own',
'52W Range',
'Perf Week',
'Perf Month',
'Perf Quarter',
'Perf Half Y',
'Perf YTD',
'Price',
'Market Cap'
]

def fundamental_metric(soup, metric):
    return soup.find(text = metric).find_next(class_='snapshot-td2').text

def get_company_name(t):
    symbol = yf.Ticker(t)
    full_company_name = symbol.info['longName']
    print('Full name of the company is: ', full_company_name)
    return full_company_name

def get_fundamental_data(df):
    for symbol in df.index:
        try:
            url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
            session = HTMLSession()
            response = session.get(url)
            soup =bs(response.content, 'html.parser')
            for m in df.columns:
                df.loc[symbol,m] = fundamental_metric(soup,m)
        except Exception as e:
            print (symbol, 'not found')
    print("Fundamental data has been successfully downloaded!")
    print(df)
    return df

def create_financial_ratio(stocklist, col=metric):
    df = pd.DataFrame(index=stocklist, columns=col)
    df = get_fundamental_data(df)

    #df['Dividend %'] = df['Dividend %'].str.replace('%', '')
    df['ROE'] = df['ROE'].str.replace('%', '')
    df['EPS Q/Q'] = df['EPS Q/Q'].str.replace('%', '')
    df['Insider Own'] = df['Insider Own'].str.replace('%', '')
    df['Inst Own'] = df['Inst Own'].str.replace('%', '')
    df['Perf Week'] = df['Perf Week'].str.replace('%', '')
    df['Perf Month'] = df['Perf Month'].str.replace('%', '')
    df['Perf Quarter'] = df['Perf Quarter'].str.replace('%', '')
    df['Perf Half Y'] = df['Perf Half Y'].str.replace('%', '')
    df['Perf YTD'] = df['Perf YTD'].str.replace('%', '')
    df['Perf YTD'] = df['Perf YTD'].astype(float)
    df = df.sort_values(by='Perf YTD', ascending=False)
    print(df)
    return df
    flag = 0
    today = datetime.now()
    if today.day == 1 and today.month%3 == 1 :
        print("It's the first day of this quater!")
        return flag
    else: 
        flag = 1
        print("Today is not the first day of this quarter!")
        return flag
    
def refactor_dataframe():
    financial_ratio = create_financial_ratio(stockSymbols)
    df = financial_ratio
    print(df['Price'])
    return df

def get_financial_ratio(f=finantial_ratio_file_name):
    # data = web.DataReader(stocks, 'yahoo', start, end)[col]
    # data = pdr.get_data_yahoo(stocks, 'yahoo', start,end)[col]
    try:
        data = pd.read_csv(f)
        print(data.to_string())
    except:
        print('did not find data! ')
    round_data = np.round(data, decimals=2)
    html = """\
    <html>
      <head></head>
      <body>
        {0}
      </body>
    </html>
    """.format(round_data.to_html())
    print(html)
    return html


def send_mail(body, portfolio_name):
    qq_password = os.getenv("QQ_PASSWORD")   # Assuming the password is stored in an environment variable
    message = MIMEMultipart()
    # message['Subject'] = 'Daily Price Change of My Stock List!'
    message['Subject'] = 'Daily Fundamental Data of ' + portfolio_name.upper()  + ' Portfolio !'
    message['From'] = '156709406@qq.com'
    message['To'] = '156709406@qq.com'

    body_content = body
    message.attach(MIMEText(body_content, "html"))
    msg_body = message.as_string()

    server = SMTP('smtp.qq.com', 587)
    server.starttls()
    print('Get connected to qq!')


    time.sleep(10)
    print('Wait for 10 sec before login to mail server!')
    server.login(message['From'], qq_password)
    print('Successfully log in to qq!')

    time.sleep(10)
    print('Wait for 10 sec before sending the email!')
    server.sendmail(message['From'], message['To'], msg_body)
    server.quit()
    print('Email has been sent!')

# def cmd():
#     for i in range(len(namelist)):
#         finantial_ratio_file_name = str(namelist[i]) + "_finantial_ratio_"  + timestr + ".csv"
#         financial_file = get_financial_ratio( finantial_ratio_file_name)
#         send_mail(financial_file , namelist[i])
#         print(namelist[i])
#         i = i + 1
#         finantial_ratio_file_name = ""


def cmd():
    for j in range(len(namelist)):
        temp_portfolio_name=(config.get(str(namelist[j]).upper(), namelist[j])).split(',')
        print("###################Start to print the content of each portfolio#####################")
        print(temp_portfolio_name)
        data = create_financial_ratio(temp_portfolio_name)
        finantial_ratio_file_name = str(namelist[j]) + timestr + ".csv"
        file_path = '/tmp/' + finantial_ratio_file_name
        data.to_csv(file_path, index=True, header=True)
        print("{} has been saved successfully.".format(finantial_ratio_file_name))
        financial_file = get_financial_ratio(file_path)
        send_mail(financial_file, str(namelist[j]))
        print("###################Job is completed successfully!#####################")

def lambda_handler(event, context):
    cmd()


