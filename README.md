# What this project does?
When you have a margin account with Interactive Brokers, you are able to sell both stock or options.
For stock, if you do not own the share of stock, then you will have to borrow it from the brokerage. This is termed "selling short".
For options, you are required to put up a certain amount of money as collateral in case you realize a loss. This is calculated by the brokerage and termed "margin".
You can also use margin if you are buying stock (not options). In this situation, the brokerage will only require you to set aside a certain percentage of the stock price.
Interactive Brokers (IB) will tell you that you can check margin percentages in Trader Workstation by pulling up the description page or checking other various places.
These percentages are just flat out incorrect. 
Most show the default percentage of 25% for long and 30% for short. These are the "beginning" values that stocks are defaulted to unless IB changes it.
Some show higher amounts, but in my observations, these amounts still are not correct.
Over the years, Interactive Brokers (IB) has adjusted these percentages at various times, and does not bother to update this information.
So this package is a simple python script that plugs into their API using the IB_Insync wrapper to pull margin information and calculate the correct percentages.

# There are a few requirements in order to pull the percentages:

(1) You must have a margin account with Interactive Brokers that has over $2,000. Even if your account says margin, they are not allowed to extend margin if you are below this amount.

(2) You must install Python onto your computer.

(3) You must install Trader Workstation

(4) You must install IB_Insync.

(5) Inside Trader Workstation, you must enable socket clients and have a socket port that matches the python code. We will use 7496. Make sure "Read-Only API" is NOT checked.

(6) You must have Trader Workstation up and running in the background.

(7) OPTIONAL: If you want the software to automatically attempt to pull the stock price, you'll need to subscribe to market data. See the very last section for recommended data subscriptions. The code has the ability to manually enter the price as well.


# What is Margin?
Simply put, the margin percentage tells you how much of the potential loss you have to pay for yourself. This is only relevant if your account type is a margin account.
For a stock, the potential loss matches the price of the stock. Therefore, a 30% initial margin on a $100 stock means you must have $30 in your account to buy the stock.
Due to the spotty download issues of IB, this code does not look at option margin. However, margin for ATM % option typically approximates the same amount as the stock.
As the option gets further ITM, the brokerage requires you put up more of the potential loss. As it gets further OTM, they will require less. The floor amount is 10% of the potential loss.

# What is the difference between initial margin and maintenance margin?
Initial margin is what you need to have in your account in order to initially take out the position.
Maintenance is what is needed to be maintained in your account after it is taken out to avoid the brokerage either (1) auto-close your position, or (2) request more cash be deposited (margin call)
IB claims to not do margin calls but it is reported that they provide multiple notification of pending margin issues and send notices asking you deposit more money, which is essentially a margin call.

# If you are using IB Gateway
You'll have to add an "account" parameter to the Order() class. Here is an example:

    action = Order(
            action = direction,
            totalQuantity = 1,
            orderType = orderType,   # 'MKT' or 'LMT'
            lmtPrice = limitPrice,
            tif = 'GTC',
            outsideRth = True,
            account = ACCOUNT_NUMBER
    )

# Some notes on using this script:
(1) Note that Interactive Brokers provides two different accounts: a real account, and a "paper" account. 
    The "paper" account is a fake account that is suppose to simulate the real environment for testing strategies.
    However, IB does not update the paper account with the lastest margin percentages.
    Therefore, this should only be run while a real account is pulled up in Trader Workstation. Running with a paper account pulled up will result in incorrect information.
    This script will not place any trades, it will just go in and pull margin data.

(2) The code goes into your Trader Workstation, pulls up a pretend order for 1 share of whichever stock or contract is specified, pulls up the Order Preview window,
    and pulls the margin data from that screen.
    This means that the percentages are ALWAYS based on the margin affect as it pertains to your account at that moment in time.
    If you have active positions in your account, the margin percentages could show lower than what it is in reality.
    It is believed that if the positions are ONLY stock, the percentages should not be affected and the correct percentages will show.
    However, if you have option contracts in your account with the same underlying symbol that you are attempting to check, the margin percentages on both the stock and other options 
    for the underlying will likely be lower than it would be in situations where you did not have the option positions.
    For example, if you have sold 1 call option on AAPL, when the code simulates 1 share of AAPL stock, it is believed the margin requirements will be lower due to a hedging effect.
    While IB's margin percentages generally do not change very often, the margin percentages could change for you if you have option positions in the same underlying you are checking, 
    due to a hedging effect.

(3) Price data for IB is very spotty. Regular trading hours are from 9:30 am to 4:00 pm EST and this is when you'll be able to download the most stock prices. Outside of regular market hours,
    the software does not return price data for some stocks. If you run the code when the market is closed, you may get correct data or you may get errors and NaN. 
    The data will not be wrong in the after hours, it just may not be available.
    A price override has been built into the software so that you can manually enter all of the prices and not worry about it.
    To enable this feature, turn enable_stock_price_override to TRUE. If FALSE, it will simply skip the symbol if it cannot pull stock data.
    If override is enabled, make sure the enter price data for ALL symbols and in the same exact order they are listed in the symbol_list.
    The software will return a message to the terminal for all stocks telling you wether it obtained the stock data from IB, the price list, or it skipped.

(4) sort_by variable allows you to sort the results. you indicate the column you want to sort by. The first column is the symbol. So the first % column will be 1.

    1 = stock long initial %
    2 = stock long maintenance %
    3 = stock short initial %
    4 = stock short maintenance %

# Recommended Data Subscriptions

Here is what I am subscribed to that allow for data of stocks and options:

**US Securities Snapshot and Futures Value Bundle**  
This service will deliver NBBO snapshot quotes for all listed US equity issues as well as top of book data for CME Group Futures. Also includes Dow Jones Industrial Average, S&P 500 Index, and OTC Markets quotes. Note, US Equity NBBO snapshot quotes will cost an additional 0.01 USD above the listed subscription price and waiver.  
USD 10.00 /Month  
A monthly USD 10.00 fee will be waived whenever the monthly commissions generated in the account reaches USD 30.00.  

**US Equity and Options Add-On Streaming Bundle**  
Includes streaming realtime quotes for NYSE (CTA/Network A), AMEX (CTA/Network B), NASDAQ (UTP/Network C), and OPRA (US Options). In order to subscribe to US Equity and Options Add-On Streaming Bundle (NP), the user must already be subscribed to US Securities Snapshot and Futures Value Bundle (NP).  
USD 4.50 /Month  

**Cboe One Add-On Bundle**  
Realtime streaming quotes from the four Cboe US equity exchanges. In order to subscribe to Cboe One Add-On Bundle (NP,L1), the user must already be subscribed to US Securities Snapshot and Futures Value Bundle (NP). Fee is waived if commissions generated are greater than USD 5.00. Requires TWS Version 978 and above.  
USD 1.00 /Month  
A monthly USD 1.00 fee will be waived whenever the monthly commissions generated in the account reaches USD 5.00.  
