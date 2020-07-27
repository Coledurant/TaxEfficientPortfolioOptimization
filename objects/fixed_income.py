import pandas as pd
import numpy as np
import datetime
from constants import *
from tools.get_datetime_index import get_datetime_index


class MunicipalBond(object):

    '''
    '''

    def __init__(self, investor_obj, initial_margin, initial_datetime_str, maturity_date, bond_yield=0.015, period = 'semiannual', rating = 'AAA', bond_federal_tax_rate = 0, bond_state_tax_rate = 0, bond_local_tax_rate = 0):

        self.investor_obj = investor_obj
        self.initial_margin = initial_margin
        self.initial_datetime = datetime.datetime.strptime(initial_datetime_str, DT_STRING_FORMATTER)
        self.maturity_date = maturity_date
        self.bond_yield = bond_yield
        self.period = period
        self.rating = rating
        self.bond_federal_tax_rate = bond_federal_tax_rate
        self.bond_state_tax_rate = bond_state_tax_rate
        self.bond_local_tax_rate = bond_local_tax_rate

        self.tax_equivalent_yield = self.bond_yield / ( 1 - self.investor_obj.federal_tax_rate )

        self.set_payout_frame()

        self.investment_category = 'Fixed Income'
        self.investment_sector = 'US Investment Grade Tax Exempt'
        self.name = f'Muni Bond ${self.initial_margin:,} {self.bond_yield*100}% {self.initial_datetime} - {self.maturity_date}'

        self.portfolio_print_exp =  "Muni yield of {} % maturity date at {}".format(round(self.bond_yield * 100, 2), self.maturity_date)


    def __str__(self):

        return "{} initial value | municipal bond with yield of {} % and maturity date at {}".format(self.initial_margin, round(self.bond_yield * 100, 2), self.maturity_date)

    def set_payout_frame(self):

        '''
        Returns tax free payout frame
        '''

        payout_periods = get_datetime_index(self.maturity_date, self.period, set_month_place = 'begin')

        payout_df = pd.DataFrame(index = payout_periods, columns = ['Coupon', 'Federal Tax', 'State Tax', 'Local Tax', 'Total Return', 'Net Gain'])

        if self.period == 'semiannual':
            payout_df['Coupon'] = (self.bond_yield / 2) * self.initial_margin
        elif self.period == 'annual':
            payout_df['Coupon'] = self.bond_yield * self.initial_margin
        else:
            pass

        for tax_level, tax_r in {'Federal Tax':self.bond_federal_tax_rate, 'State Tax':self.bond_state_tax_rate, 'Local Tax':self.bond_local_tax_rate}.items():

            payout_df[tax_level] = tax_r * payout_df['Coupon']

        payout_df['Coupon'] = payout_df['Coupon'] - payout_df['Federal Tax'] - payout_df['State Tax'] - payout_df['Local Tax']

        payout_df['Total Return'] = [np.sum(list(payout_df['Coupon'][:x])) for x in iter(payout_df.index)]

        payout_df['Net Gain'] = payout_df['Total Return'] - self.initial_margin
        payout_df.loc[payout_df.index[-1], 'Net Gain'] += self.initial_margin

        self.payout_frame = payout_df

        return payout_df



    def calculate_return(self):

        '''


        FIXME


        '''
        try:
            self.investment_return
        except AttributeError:
                self.investment_return = np.random.randint(-100,100) / 100

        return self.investment_return



    def get_current_value(self):

        return self.initial_margin * (1 + self.calculate_return())
