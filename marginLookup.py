from ib_insync import *
import random
import pandas as pd
import math

def connectToIBKR():
    # --- CONNECTING TO INTERACTIVE BROKERS ---
    print("\nConnecting to Interactive Brokers...",'\n')
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=random.randint(1,99))
    return ib

def format_stock_for_IBKR(symbol):
    stock_IBKR_Formatted = Stock(
        symbol=symbol,
        exchange='SMART/AMEX',
        currency='USD'
    )
    return stock_IBKR_Formatted

def connectToStockData_IBKR(symbol,stock_IBKR_Formatted,enable_stock_price_override):
    # turning on stock data
    stockData = ib.reqMktData(
        contract=stock_IBKR_Formatted,
        genericTickList='',
        snapshot=False,
        regulatorySnapshot=False
    )

    ib.sleep(1)

    #print('\n',stockData)

    if math.isnan(stockData.last):
        if enable_stock_price_override:
            stockPrice = last_price_override[count]
            print(f'not able to pull {symbol} from IB. Used price override of {last_price_override[count]}...')
    else:
        stockPrice = stockData.last
        print(f'successfully pulled {symbol} price of {stockPrice} from IB...')

    return stockPrice

# --- connecting to IBKR ---
ib = connectToIBKR()

# --- variables ---
symbol_list = ['AAPL','SPY','NIO','WPC','BABA','GME','AMC','COIN','MSFT','QQQ']
enable_stock_price_override = True                                                                  # see note at bottom. If False, last_price_override will not work.
last_price_override = [186,433,8.44,66.57,84.88,23.60,4.04,61.26,335.02,362.54]                      # See note at bottom. FILL OUT PRICE DATA FOR ALL SYMBOLS AND IN THE SAME ORDER.
checking = ['long','short']
sort_by =  2                                                                                           # this sorts the results highest to lowest by the specified column.
# columns:
# 2 = stock long initial
# 3 = stock long maint
# 4 = stock short initial
# 5 = stock short maint

# --- downloading margin percentages for stock ---
symbol_column = [] 
marginPercentagesPulledFromIBKR = []
count = 0
for symbol in symbol_list:
    try:
        # you cannot simply use strings for the tickers in IBKR. this formats it the correct way.
        stock_IBKR_Formatted = format_stock_for_IBKR(symbol)

        # pulls stock data from IBKR. used to calculate percentage.
        stockPrice = connectToStockData_IBKR(symbol,stock_IBKR_Formatted,enable_stock_price_override)

        marginInfo = []
        for direction in checking:

            if direction == 'long':
                direction_order = 'buy'
            elif direction == 'short':
                direction_order = 'sell'
            else:
                print("error with the direction variable. Only 'long' or 'short' can be used.")
            
            order = MarketOrder(
                action=direction_order,
                totalQuantity=1,
                tif='GTC'
            )

            # whatIfOrder() is the only way I'm aware of that will pull margin data. It also can pull expected commissions.
            whatIfOrder = ib.whatIfOrder(stock_IBKR_Formatted, order)

            initial_margin = float(whatIfOrder.initMarginChange)
            maint_margin = float(whatIfOrder.maintMarginChange)

            initial_margin_perc = abs(round((initial_margin / stockPrice) * 100, 0))
            maint_margin_perc = abs(round((maint_margin / stockPrice) * 100, 0))

            marginInfo.append((initial_margin_perc, maint_margin_perc))
            symbol_column.append(symbol)
            
        mergedTuple = marginInfo[0] + marginInfo[1]
        marginPercentagesPulledFromIBKR.append(mergedTuple)
        print(marginPercentagesPulledFromIBKR)
        #print(symbol_column)

        count += 1

    except:
        print(f'issue with {symbol}. skipping...','\n')
        continue


# removing duplicates from symbol list.
seen = set()
symbol_column = [x for x in symbol_column if not (x in seen or seen.add(x))]

# moving information to Pandas Dataframe
df_stock = pd.DataFrame(
    {
        'Symbol': symbol_column,
        'stock long initial': [t[0] for t in marginPercentagesPulledFromIBKR],
        'stock long maint': [t[1] for t in marginPercentagesPulledFromIBKR],
        'stock short initial': [t[2] for t in marginPercentagesPulledFromIBKR],
        'stock short maint': [t[3] for t in marginPercentagesPulledFromIBKR]
    }
)

# # this sorts the results highest to lowest by the specified column. see the sort_by variable above.
df_stock.sort_values(df_stock.columns[sort_by], ascending=False, inplace=True)
df_stock.reset_index(inplace=True,drop=True)

# prints results to terminal
print(df_stock)

# --- NOTES ---
# LAST PRICE OVERRIDE: Margine $$ is available all the time. However, the ability to pull price data from IB is spotty.
# it is most spotty when the market is closed or in the after hours trading period.
# Therefore, the LAST PRICE OVERRIDE variable is provided so that you can enter the correct price. This will ensure you will get percentages for all your stocks.
# however, it does require some manual work. During the off-hours though, the stock price will not change, so this is the only solution.
# the code looks to see if it can pull a price from IB. If it can, it will do that automatically. If not, it will use your override value.
# please make sure to enter a price in the override column for all tickers, and list it in the same order that the stocks are listed in.
