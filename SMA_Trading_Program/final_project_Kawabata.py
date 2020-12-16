# Stock Algorithim Program
# Masashi Kawabata
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def read_data():
    voo = pd.read_csv("VOO.csv", header = 0)
    return voo

def data_statistics():
    data = read_data()
    summary = pd.DataFrame.describe(data).round(2) #OP method that shows all the summary statistics
    print("Following result shows the summary statistics: \n")# Note that 50% shows the median number of the dataset
    print(summary)
    print('\n')

def get_sma(dataframe):
    sma10 = [0] * len(dataframe)  # Creating empty int list to get computed numbers
    df = dataframe
    df['SMA10'] = df.Open.rolling(10).mean().fillna(0).round(2) #rolling 10D average rounded in 2 decimal places plus NaN replaced to 0
    sma10 = df['SMA10'].tolist()
    return sma10

def make_transaction(account,price,qty,buy):
    qty_can_afford = account['Balance'] // price #If you cannot afford 10 shares with balance shortage
    qty_to_buy = qty #Used for buy decision
    qty_to_sell = qty # Used for sell decision
    if qty_can_afford < qty:
        qty_to_buy = qty_can_afford # Conditional that if we cannot afford 10 shares, qty to buy becomes any shares that we can afford.
    if account['Stock Quantity'] < qty:
        qty_to_sell = account['Stock Quantity'] #If we don't have enough qty of shares, sell remaining shares

    if buy == True: #When trade function recognizes that open price is 5% higher than 10 day sma
        if account["Balance"] > qty_to_buy * price:
            account["Balance"] = account["Balance"] - qty_to_buy * price
            account["Stock Quantity"] += qty_to_buy
        else:
            account['Balance'] = account['Balance'] - qty_to_buy * price
            account["Stock Quantity"] += qty_to_buy
        print(f"The program has purchased the stock at the price of {price} dollars per share.")
        print(f"It has purchased {qty_to_buy:.0f} number of shares.")
        print(f"Current balance is {account['Balance']:.2f} dollars.") #Program didn't round all results so used this additional method
        print(f"Remaining stock quantity is {account['Stock Quantity']}. \n")

    else:
        if account["Stock Quantity"] >= qty_to_sell:
            account["Balance"] = account["Balance"] + qty_to_sell * price
            account["Stock Quantity"] -= qty_to_sell
        else:
            account["Balance"] = account["Balance"] + qty_to_sell * price
            account["Stock Quantity"] = 0
        print(f"The program has sold the stock at the price of {price} dollars per share.")
        print(f"It has sold {qty_to_sell:.0f} number of shares.")
        print(f"Current balance is {account['Balance']:.2f} dollars.")
        print(f"Remaining stock quantity is {account['Stock Quantity']}. \n" )

def trade(dataframe, sma, account):
    trade_lst = [] #empty list to add transaction details
    df = dataframe
    df['Open'] = df.Open.round(2)
    open_pri = df['Open'].tolist()
    sma_pri = sma
    for i in range(10, len(dataframe)):#skipping first 10 days since sma is unavailable
        percent_chg = (open_pri[i] - sma_pri[i])/sma_pri[i] #Calculate the % change
        if percent_chg >= 0.05:
            make_transaction(account, open_pri[i], 10, False)#Sells the stock
            trade_lst.append(-1)
        elif percent_chg <= -0.05:
            make_transaction(account, open_pri[i], 10, True)#Buys the shares
            trade_lst.append(1)
        else:
            trade_lst.append(0)
    return trade_lst

def make_plot(dataframe, sma):
    df = dataframe

    d = df['Date'].tolist() #convert dates into list
    xaxis = [datetime.strptime(x, '%m/%d/%Y') for x in d]

    df['Buy'] = np.where(((df['Open'] - sma)/sma) <= -0.05, 1, 0) #find entries with buy condition
    buy_df = df[df['Buy'] == 1] #make new dataframe with entries where you buy
    b = buy_df['Date'].tolist()
    buy = [datetime.strptime(x, '%m/%d/%Y') for x in b] #get dates for these entries


    df['Sell'] = np.where(((df['Open'] - sma)/sma) >= 0.05, 1, 0) #find entries with sell condition
    sell_df = df[df['Sell'] == 1] #make new dataframe with entries where you sell
    sell_df = sell_df.iloc[10:] #remove first 10 days for lack of SMA calculation
    s = sell_df['Date'].tolist()
    sell = [datetime.strptime(x, '%m/%d/%Y') for x in s] #get dates for these entries

    plt.figure(figsize=(15,6))
    plt.title('VOO ETF vs. 10D SMA Data with Sell/Buy Algorithim')
    plt.plot(xaxis, df['Open'], linestyle= '-', color ='black', label ='VOO')
    plt.plot(xaxis, sma, linestyle = '--', color = 'green', linewidth = 2.0, label = '10 day SMA')
    plt.scatter(buy, buy_df['Open'] ,label='Buy', color='green', s=50, marker="o")
    plt.scatter(sell, sell_df['Open'], label='Sell', color='red', s=50, marker="o")
    plt.ylim(150, 400)
    plt.legend()
    plt.show()

def main():
    stock_data = read_data()
    print(stock_data)
    stats = data_statistics()
    sma = get_sma(stock_data)
    balance = 10000 #Setting initial balance of 100K
    stkqty = 0 #Don't own a stock in the beginning
    account = {"Balance": balance, "Stock Quantity": stkqty}
    print(trade(stock_data, sma, account))
    make_plot(stock_data, sma)

main()