import pandas as pd
import yfinance as yf
import datetime
import numpy as np
from constants import *


class StockPosition(object):

    def __init__(self, ticker, num_shares, initial_datetime_str):

        self.ticker = ticker
        self.num_shares = num_shares


        #FIX FOR BETTER PRICING DATA
        self.buy_price = self.get_last_min_close_price()
        self.initial_datetime = datetime.datetime.strptime(initial_datetime_str, DT_STRING_FORMATTER)

        self.initial_margin = round(self.buy_price * self.num_shares,2)



        self.investment_category = 'Equity'

        ticker = yf.Ticker(self.ticker)
        ticker_info = ticker.get_info()
        self.market_cap = ticker_info['marketCap']
        self.country = ticker_info['country'].lower()


        self.set_investment_sector()







        self.name = f'{self.ticker} {self.num_shares:,} @ ${self.buy_price:,} (${self.initial_margin:,})'

        self.portfolio_print_exp = "{} shares of {} at ${}".format(self.num_shares, self.ticker, self.buy_price)


    def calculate_return(self):

        '''


        FIXME


        '''

        last_close_price = self.get_last_min_close_price()

        ticker = yf.Ticker(self.ticker)
        actions = ticker.actions
        dividend_amounts = np.sum(actions.loc[self.initial_datetime:]['Dividends'])

        return ((last_close_price - self.buy_price) + dividend_amounts) / self.buy_price




    def get_current_value(self):

        return self.initial_margin * (1 + self.calculate_return())

    def get_last_min_close_price(self):

        ticker = yf.Ticker(self.ticker)
        df = ticker.history(period="1",interval="1m")


        last_min_close_price = df.iloc[-1]['Close']


        return last_min_close_price


    def set_investment_sector(self):

        os.chdir(DATA_DIR)


        investment_sectors_df = pd.read_csv('ticker_investment_sector.csv', index_col=0)

        try:
            investment_sector = investment_sectors_df.loc[self.ticker.upper()]['investment_sector']
            self.investment_sector = investment_sector
        except KeyError:

            print("COULD NOT FIND SECTOR IN CSV FILE")

            with open('emerging_markets_list.txt', 'r') as f:
                r = f.read().strip()
            emerging_markets_list = [country.lower() for country in r.split(',')]

            if self.country == 'united states':





                # FIXME
                growth_value = 'Growth'






                if self.market_cap > 10000000000:
                    self.investment_sector = 'US Large Cap {}'.format(growth_value)
                else:
                    self.investment_sector = 'US Small Cap {}'.format(growth_value)

            elif self.country in emerging_markets_list:
                self.investment_sector = 'Emerging Markets'
            else:
                self.investment_sector = 'International Developed Equity'

        finally:

            os.chdir(ROOT_DIR)
