#!/usr/bin/env python
import pandas as pd
import requests
import csv
from datetime import datetime, timedelta, date
import time
import os
import numpy as np
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

CONFIG_FILE = './config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
symbols = ['TSLA','AAPL','ABNB','AMD','ARM','AMZN',\
           'CVNA','COIN','LCID','LYFT','MSFT','META','GOOGL','NIO',\
           'RVN','ROKU','SNAP','SQ','OPEN','PANW','NFLX','NVDA']  # Add more symbols as needed
qq_password = os.getenv("QQ_PASSWORD") 
api_key = os.getenv("API_KEY") 
horizon = "3month"
timestr = time.strftime("%Y-%m-%d")
today = datetime.today()
output_file_path = "/tmp/" + "earnings_report_" + timestr + ".csv"
# namelist = ['symbols']

def get_earnings_date():
    data = []
    api_key = os.getenv("API_KEY")   # Assuming the password is stored in an environment variable

    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol={symbol}&horizon={horizon}&apikey={api_key}"
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for row in my_list:
                data.append([symbol] + row)

    # Create a DataFrame from the data list
    columns = ['Symbol'] + data[0][1:]  # Use the header from the first row
    df = pd.DataFrame(data[1:], columns=columns)

    # Remove rows containing the value 'name'
    df = df[~df.apply(lambda row: 'name' in row.values, axis=1)]

    # Drop the duplicate column 'symbol'
    df = df.loc[:, ~df.columns.duplicated()]

    # Remove rows with None values in the 'reportDate' column
    df = df.dropna(subset=['reportDate'])

    # Save the DataFrame to a CSV file
    # output_file_path = "./calendar_data.csv"
    df.to_csv(output_file_path, index=False)

def format_report(f=output_file_path):
    # data = web.DataReader(stocks, 'yahoo', start, end)[col]
    # data = pdr.get_data_yahoo(stocks, 'yahoo', start,end)[col]
    try:
        df = pd.read_csv(f)
        df = df.drop("Symbol", axis=1)
        df = df.sort_values(by='reportDate')

        ############ add a new column of days in difference ############
        df['reportDate'] = pd.to_datetime(df['reportDate'])
        df['days_difference'] = (df['reportDate'] - today ).dt.days

        data = df.sort_values(by='reportDate')
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

def send_mail(body):
    message = MIMEMultipart()
    # message['Subject'] = 'Daily Price Change of My Stock List!'
    message['Subject'] = 'Earnings Report Calendar!'
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


def cmd():
        print("###################Start to generate earnings report release date#####################")
        get_earnings_date()
        calendar_file = format_report()
        send_mail(calendar_file)
        print("###################Job is completed successfully!#####################")

def lambda_handler(event, context):
    cmd()


