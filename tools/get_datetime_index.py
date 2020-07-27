import pandas as pd
import datetime
from constants import *

def get_datetime_index(end_date_str, annual_frequency = 'semiannual', set_month_place = None):

    end_datetime = datetime.datetime.strptime(end_date_str,DT_STRING_FORMATTER)

    if annual_frequency == 'semiannual':
        month_frequency = 6
        dr_periods = (end_datetime.year - datetime.datetime.now().year)*2
    elif annual_frequency == 'annual':
        month_frequency = 12
        dr_periods = end_datetime.year - datetime.datetime.now().year
    else:
        print('Fix month frequency')

    if set_month_place is None:
        return_date = pd.date_range(start=datetime.datetime.now(), end=end_datetime, periods=dr_periods)
    elif set_month_place == 'begin':
        return_date = pd.date_range(end=end_datetime, freq=pd.offsets.MonthBegin(month_frequency), periods=dr_periods)
    elif set_month_place == 'end':
        return_date = pd.date_range(end=end_datetime, freq=pd.offsets.MonthEnd(month_frequency), periods=dr_periods)
    else:
        return None

    return return_date




if __name__ == '__main__':

    get_datetime_index('02-01-2023 00:00:00', annual_frequency = 'semiannual', set_month_place = 'begin')
