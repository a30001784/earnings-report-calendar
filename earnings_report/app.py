#!/usr/bin/env python
import pandas as pd
import requests
import csv

symbols = ['TSLA','AAPL','AMD','ARM','AMZN','MSFT','META','GOOGL','NIO','SNAP','OPEN','NFLX','NVDA']  # Add more symbols as needed
horizon = "3month"
earnings_report_file_path = "earnings_report_" + timestr + ".csv"

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
    output_file_path = "/tmp/calendar_data.csv"
    df.to_csv(output_file_path, index=False)



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


def cmd():
    for j in range(len(namelist)):
        temp_portfolio_name=(config.get(str(namelist[j]).upper(), namelist[j])).split(',')
        print("###################Start to print the content of each portfolio#####################")
        print(temp_portfolio_name)
        data = create_financial_ratio(temp_portfolio_name)
        finantial_ratio_file_name = str(namelist[j]) + timestr + ".csv"
        file_path = '/tmp/' + earnings_report_file_path
        data.to_csv(file_path, index=True, header=True)
        print("{} has been saved successfully.".format(finantial_ratio_file_name))
        financial_file = get_financial_ratio(file_path)
        send_mail(financial_file, str(namelist[j]))
        print("###################Job is completed successfully!#####################")

def lambda_handler(event, context):
    cmd()


