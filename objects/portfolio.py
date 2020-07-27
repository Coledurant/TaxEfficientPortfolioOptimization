import numpy as np
import datetime
from tools.print_helpers import *




class Portfolio(object):

    def __init__(self, investor_obj, NAV):

        self.investor_obj = investor_obj
        self.NAV = NAV

        self.positions = []

        self.calculate_portfolio_weights()

        self.portfolio_returns_over_time = {datetime.datetime.now():0.0}
        self.portfolio_values_over_time = {datetime.datetime.now():self.NAV}


    def __str__(self):

        return "NAV: {}\nNumber of Positions: {}".format(self.NAV, len(self.positions))

    def calculate_portfolio_weights(self):


        df = self.investor_obj.allocation_frame.copy()

        df.set_index('investment_category', inplace=True)

        self.portfolio_weights = {'Equity':df.loc['Equity'][self.investor_obj.portfolio_aggresiveness],
                                'Fixed Income':df.loc['Fixed Income'][self.investor_obj.portfolio_aggresiveness],
                                'Cash':df.loc['Cash'][self.investor_obj.portfolio_aggresiveness],
                                'Alternatives':df.loc['Alternatives'][self.investor_obj.portfolio_aggresiveness]}

    def print_positions(self, line_length):

        print('\n')
        print(centered_text("Positions", line_length))
        print('-' * line_length)
        print(tuple_space_set_length(("INITIAL VALUE","INVESTMENT"), line_length))
        print('-' * line_length)

        for investment_category, portfolio_weight in self.portfolio_weights.items():

            print('\n')
            print(centered_text("{} ({} %)".format(investment_category.capitalize(), round(portfolio_weight * 100, 2)), line_length))
            print('\n')

            for position in [p for p in self.positions if p.investment_category == investment_category]:


                print(tuple_space_set_length((str(position.initial_margin),position.portfolio_print_exp), line_length))


    def add_position(self, position):

        # Checking if there is enough margin to fill
        if position.initial_margin > self.get_margin_available():
            return False
        else:
            self.positions.append(position)

            self.investor_obj.save_to_pickle()

            return True





    def get_margin_available(self):

        return self.NAV - np.sum([position.initial_margin for position in self.positions])

    def get_margin_used(self):

        return np.sum([position.initial_margin for position in self.positions])

    def calculate_weighted_return(self):

        weighted_return = np.sum([asset.calculate_return() * (asset.initial_margin / self.NAV) for asset in self.positions])

        self.portfolio_returns_over_time[datetime.datetime.now()] = weighted_return

        return weighted_return



    def get_current_value(self):

        '''
        Assumes never adding or taking away from NAV
        '''

        current_value = self.NAV * (1+self.calculate_weighted_return())

        self.portfolio_values_over_time[datetime.datetime.now()] = current_value

        return current_value
