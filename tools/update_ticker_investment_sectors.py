

'''


Run this to update ticker_investment_sector.csv


'''




import requests
from bs4 import BeautifulSoup
import pandas as pd
from constants import *

def get_tickers(url):

    url = url + '?page={}'

    page_num = 1

    complete_tickers_list = []

    while True:

        print(url.format(page_num))
        soup = BeautifulSoup(requests.get(url.format(page_num)).content, 'lxml')

        tickers = [x.text for inum,x in enumerate(soup.findAll('span', attrs={'class':'mdc-data-point mdc-data-point--string'})) if inum%2 == 1]

        if len(tickers) == 0:
            break

        complete_tickers_list += tickers

        page_num += 1

    return complete_tickers_list




if __name__ == '__main__':



    sector_url_dict = {
        'US Large Cap Growth':'https://www.morningstar.com/large-cap-growth-stocks',
        'US Large Cap Value':'https://www.morningstar.com/large-cap-value-stocks',
        'US Large Cap Core':'https://www.morningstar.com/large-cap-core-stocks',
        'US Mid Cap Value':'https://www.morningstar.com/mid-cap-value-stocks',
        'US Mid Cap Growth':'https://www.morningstar.com/mid-cap-growth-stocks',
        'US Mid Cap Value':'https://www.morningstar.com/mid-cap-value-stocks',
        'US Mid Cap Core':'https://www.morningstar.com/mid-cap-core-stocks',
        'US Small Cap Growth':'https://www.morningstar.com/small-cap-growth-stocks',
        'US Small Cap Value':'https://www.morningstar.com/small-cap-value-stocks',
        'US Small Cap Core':'https://www.morningstar.com/small-cap-core-stocks',
    }

    sector_tickers_dict = dict()
    ticker_sector_dict = dict()
    for sector, url in sector_url_dict.items():

        print(sector)
        ticks = get_tickers(url)
        print(len(ticks))

        for ticker in ticks:
            ticker_sector_dict[ticker] = sector


    df = pd.DataFrame.from_dict(ticker_sector_dict, 'index', columns=['investment_sector'])

    os.chdir(DATA_DIR)

    df.to_csv('ticker_investment_sector.csv')

    os.chdir(ROOT_DIR)
