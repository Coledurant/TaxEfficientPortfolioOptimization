import os
import pandas as pd
from constants import *
from tools.print_helpers import *
from objects.portfolio import Portfolio
import pickle
import datetime


class Investor(object):

    '''

    '''

    def __init__(self, name, age, filing_status, annual_income, state_code, county, NAV, liquidity_tier, portfolio_aggresiveness, password = None):

        self.name = name
        self.age = age
        self.filing_status = filing_status
        self.annual_income = round(annual_income,2)
        self.state_code = state_code
        self.county = county
        self.NAV = round(NAV,2)
        self.password = password

        self.get_federal_tax_rate()


        # Setting tax sensitivity depending on federal tax rate
        self.tax_sensitivity = 'high' if self.federal_tax_rate > .20 else 'low'

        self.liquidity_tier = liquidity_tier
        self.portfolio_aggresiveness = portfolio_aggresiveness

        self.get_allocation_frame()


        # Initializing a portfolio object
        self.portfolio = Portfolio(self, self.NAV)






    def __str__(self):

        return self.name


    def get_allocation_frame(self):

        os.chdir(DATA_DIR)

        tax_sensitive_liquidity_level = '{}_tax_sensitivity_tier_{}_liq'.format(self.tax_sensitivity, self.liquidity_tier)

        frame = pd.read_excel('allocation_tables.xlsx', tax_sensitive_liquidity_level, index_col='investment_category')
        frame.reset_index(inplace=True, drop=False)

        os.chdir(ROOT_DIR)

        self.allocation_frame = frame[['investment_category',self.portfolio_aggresiveness]]

        return frame[['investment_category',self.portfolio_aggresiveness]]

    def print_profile(self):

        line_length = 80

        print('\n\n\n')
        print("#"*line_length)
        print(centered_text(self.name.upper(), line_length))
        print("#"*line_length)
        print('\n')

        for title, info in {"NAV":self.NAV,"age":self.age,"Filing Status":self.filing_status,"Annual Income":self.annual_income,"Location":"{}, {}".format(self.county, self.state_code)}.items():
            print(tuple_space_set_length((title, str(info)), line_length))

        print('\n')
        print("#"*line_length)
        print(centered_text("PORTFOLIO", line_length))
        print("#"*line_length)
        print('\n')


        print(self.portfolio)

        self.portfolio.print_positions(line_length = line_length)


        print('\n')
        print("#"*line_length)
        print('\n\n\n')

        return None


    def save_to_pickle(self):

        if not os.path.exists(PICKLED_MODELS_DIR):
            os.mkdir(PICKLED_MODELS_DIR)
        os.chdir(PICKLED_MODELS_DIR)

        model_name = self.name.replace(" ", "_").lower()

        # Creating model name folder if it does not exist
        if not os.path.exists(model_name):
            os.mkdir(model_name)
        os.chdir(model_name)

        # Saving model under model name in model name folder
        with open(model_name, 'wb') as file:
            pickle.dump(self, file)

        os.chdir(ROOT_DIR)

    @classmethod
    def read_pickled_investor(Investor, investor_name):

        model_name = investor_name.replace(" ", "_").lower()

        if not os.path.exists(PICKLED_MODELS_DIR):
            os.mkdir(PICKLED_MODELS_DIR)
        os.chdir(PICKLED_MODELS_DIR)

        if not os.path.exists(model_name):
            return False
        else:
            os.chdir(model_name)

        with open(model_name, 'rb') as file:
            pickle_model = pickle.load(file)

        print("\nThe following investor model was loaded:")

        pickle_model.print_profile()

        os.chdir(ROOT_DIR)

        return pickle_model

    def get_federal_tax_rate(self):

        '''
        Reads in csv file of 2020 tax brackets and sets federal_tax_rate
        '''

        os.chdir(DATA_DIR)
        tax_brackets = pd.read_csv('tax_brackets.csv')
        os.chdir(ROOT_DIR)

        # Turning column values into real tuples with two integers, the high and
        # low ow tax bracket values
        for col in [c for c in tax_brackets.columns if c != 'tax rate']:
            tax_brackets[col] = [tuple(int(x) for x in y[1:-1].split(',')) for y in tax_brackets[col]]


        for inum, row in tax_brackets.iterrows():

            tr = row['tax rate']
            fs_col = row[self.filing_status]

            # Finding whether or not annual income is within this tax rate tuple,
            # and setting self.federal_tax_rate to the tax rate of that row if so
            if fs_col[0] <= self.annual_income <= fs_col[1]:
                self.federal_tax_rate = tr
