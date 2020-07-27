from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly

import pandas as pd
import numpy as np
import datetime


from objects.investor import Investor
from objects.fixed_income import MunicipalBond
from objects.equity import StockPosition
from constants import *

from tools.calculate_red_green_rgb import calculate_red_green_rgb
from tools.get_polyline_fill_values import get_polyline_fill_values


flatten = lambda l: [item for sublist in l for item in sublist]

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/', methods = ['GET', 'POST'])
def index():

    if request.method == 'POST':

        data = request.form

        investor_name = data.get('investor_name')

        investor = Investor.read_pickled_investor(investor_name)

        if investor is False:

            investor_age = int(data.get('investor_age'))
            filing_status = data.get('filing_status').replace('_', ' ')
            investor_annual_income = float(data.get('investor_annual_income'))
            investor_state_code = data.get('investor_state_code')
            investor_county = data.get('investor_county')
            investor_NAV = float(data.get('investor_NAV'))
            liquidity_tier = int(data.get('liquidity_tier'))
            portfolio_aggresiveness = data.get('portfolio_aggresiveness').replace('_',' ') + ' - Strategic'
            investor_password = data.get('password')

            investor = Investor(name = investor_name, age=investor_age, filing_status = filing_status,
                                annual_income = investor_annual_income, state_code = investor_state_code,
                                county = investor_county, NAV = investor_NAV, liquidity_tier = liquidity_tier,
                                portfolio_aggresiveness = portfolio_aggresiveness, password = investor_password)
            investor.save_to_pickle()

        else:

            return render_template('account_already_exists.html')

    return render_template('index.html', **{'login_message':''})

@app.route('/signup')
def signup():

    return render_template('signup.html', **{'signup_message':''})


@app.route('/signout')
def signout():

    global investor
    investor = None

    return render_template('signout.html')

@app.route('/investor', methods = ['GET', 'POST'])
def investor_view():
    global investor

    context = dict()

    if request.method == 'POST':

        data = request.form
        investor_name = data.get('investor_name')
        investor = Investor.read_pickled_investor(investor_name)

        if investor == False:
            return render_template('signup.html', **{'signup_message':'No such account exists, please sign up'})


        if data.get('password') == investor.password:
            context['investor'] = investor

            context['investor_annual_income_comma'] = f'{investor.annual_income:,}'
            portfolio_current_balance = investor.portfolio.get_current_value()
            context['portfolio_current_balance_comma'] = f'{portfolio_current_balance:,}'
            portfolio_NAV = investor.portfolio.NAV
            context['portfolio_nav_comma'] = f'{portfolio_NAV:,}'
            margin_available = investor.portfolio.get_margin_available()
            margin_used = portfolio_NAV - margin_available
            context['portfolio_margin_available_comma'] = f'{margin_available:,}'
            context['portfolio_margin_used_comma'] = f'{margin_used:,}'
            num_open_positions = len(investor.portfolio.positions)
            context['num_open_positions_comma'] = f'{num_open_positions:,}'
            context['portfolio_return_precentage'] = round(investor.portfolio.calculate_weighted_return() * 100,2)

            if portfolio_current_balance >= portfolio_NAV:
                context['polyline_fill'] = get_polyline_fill_values(investor.portfolio.portfolio_returns_over_time)
                context['polyline_fill_stroke'] = '#8ed734'
                context['polyline_fill_arrow'] = 'M11 2.206l-6.235 7.528-.765-.645 7.521-9 7.479 9-.764.646-6.236-7.53v21.884h-1v-21.883z'

            else:
                context['polyline_fill'] = get_polyline_fill_values(investor.portfolio.portfolio_returns_over_time)
                context['polyline_fill_stroke'] = '#ff3a3a'
                context['polyline_fill_arrow'] = 'M11 21.883l-6.235-7.527-.765.644 7.521 9 7.479-9-.764-.645-6.236 7.529v-21.884h-1v21.883z'


            investor.save_to_pickle()


            return render_template('investor.html', **context)

        else:


            return render_template('incorrect_password.html')


    else:

        if investor is not None:
            context['investor'] = investor

            context['investor_annual_income_comma'] = f'{investor.annual_income:,}'
            portfolio_current_balance = investor.portfolio.get_current_value()
            context['portfolio_current_balance_comma'] = f'{portfolio_current_balance:,}'
            portfolio_NAV = investor.portfolio.NAV
            context['portfolio_nav_comma'] = f'{portfolio_NAV:,}'
            margin_available = investor.portfolio.get_margin_available()
            margin_used = portfolio_NAV - margin_available
            context['portfolio_margin_available_comma'] = f'{margin_available:,}'
            context['portfolio_margin_used_comma'] = f'{margin_used:,}'
            num_open_positions = len(investor.portfolio.positions)
            context['num_open_positions_comma'] = f'{num_open_positions:,}'
            context['portfolio_return_precentage'] = round(investor.portfolio.calculate_weighted_return() * 100,2)

            if portfolio_current_balance >= portfolio_NAV:
                context['polyline_fill'] = get_polyline_fill_values(investor.portfolio.portfolio_returns_over_time)
                context['polyline_fill_stroke'] = '#8ed734'
                context['polyline_fill_arrow'] = 'M11 2.206l-6.235 7.528-.765-.645 7.521-9 7.479 9-.764.646-6.236-7.53v21.884h-1v-21.883z'

            else:
                context['polyline_fill'] = get_polyline_fill_values(investor.portfolio.portfolio_returns_over_time)
                context['polyline_fill_stroke'] = '#ff3a3a'
                context['polyline_fill_arrow'] = 'M11 21.883l-6.235-7.527-.765.644 7.521 9 7.479-9-.764-.645-6.236 7.529v-21.884h-1v21.883z'



            investor.save_to_pickle()

            return render_template('investor.html', **context)


        return render_template('index.html', **{'login_message':'Please log in'})


@app.route('/portfolio')
def portfolio():

    global investor

    context = dict()






    assets = investor.portfolio.positions
    for asset in assets:
        asset.calculate_return()


    categories = set([asset.investment_category for asset in assets])

    df = pd.DataFrame(index = range(len(assets) + len(categories) + 1), columns = ['label', 'initial_margin', 'investment_return', 'investment_category'])
    margin_used = np.sum([asset.initial_margin for asset in assets])
    portfolio_weighted_return = round(investor.portfolio.calculate_weighted_return(),2)

    df.iloc[0] = ['Portfolio', investor.portfolio.NAV, portfolio_weighted_return, '']

    for inum, category in enumerate(categories):

        inum += 1

        category_investments = [asset for asset in assets if asset.investment_category == category]
        category_margin_used = np.sum([asset.initial_margin for asset in category_investments])

        # CHECK
        category_weighted_returns = [asset.calculate_return() * (asset.initial_margin / category_margin_used) for asset in category_investments]
        category_weighted_return = round(np.sum(category_weighted_returns),2)


        df.iloc[inum] = [category, category_margin_used, category_weighted_return, 'Portfolio']

    for inum, asset in enumerate(assets):

        inum += len(categories) + 1

        df.iloc[inum] = [asset.name, asset.initial_margin, asset.calculate_return(), asset.investment_category]





    fig = go.Figure()
    fig.add_trace(go.Sunburst(
            labels=df['label'],
            parents=df['investment_category'],
            values=df['initial_margin'],
            marker=dict(
            colors=[calculate_red_green_rgb(x) for x in df['investment_return']]),
            textfont=dict(
                family="courier new",
                size=12,
                color="white"
            )))

    fig.update_layout(height=800)

    portfolio_weighting_pie_div = plotly.offline.plot(fig, auto_open = False, output_type="div")
    context['portfolio_weighting_pie_div'] = portfolio_weighting_pie_div



    fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]], column_widths=[0.4, 0.3, 0.3])


    fig.add_trace(go.Table(
                        header=dict(values=[c for c in list(df.columns) if c != 'investment_category'],
                                    fill_color='paleturquoise',
                                    align='left'),
                        cells=dict(values=[df.label, [f'{x:,}' for x in df.initial_margin], df.investment_return],
                                   fill_color='lavender',
                                   align='left')), 1,1)

    df = investor.allocation_frame.copy()
    df['parents'] = ['','Equity','Equity','Equity','Equity','Equity','Equity','Equity','Equity','Equity','Equity','Equity','','Fixed Income','Fixed Income','Fixed Income','Fixed Income','Fixed Income','Fixed Income','Fixed Income','','','Alternatives','Alternatives']
    print(df)

    fig.add_trace(go.Sunburst(
            labels=df['investment_category'],
            parents=df['parents'],
            values=df[investor.portfolio_aggresiveness],

            textfont=dict(
                family="courier new",
                size=12,
                color="white"
            )), 1,2)


    df.set_index('investment_category', inplace=True)
    df[investor.portfolio_aggresiveness] = 0

    # asset_ic_dict = {ac:0 for ac in investor.portfolio.portfolio_weights}
    asset_ic_dict = {ac:0 for ac in df.index}

    for asset in assets:

        asset_ic_dict[asset.investment_category] += asset.initial_margin
        asset_ic_dict[asset.investment_sector] += asset.initial_margin

    asset_ic_dict = {a:b/investor.portfolio.NAV for a,b in asset_ic_dict.items()}


    for cat,perc in asset_ic_dict.items():

        df.loc[cat, investor.portfolio_aggresiveness] = perc

    df.loc['Cash', investor.portfolio_aggresiveness] = investor.portfolio.get_margin_available() / investor.portfolio.NAV



    df.reset_index(inplace=True, drop=False)

    fig.add_trace(go.Sunburst(
            labels=df['investment_category'],
            parents=df['parents'],
            values=df[investor.portfolio_aggresiveness],

            textfont=dict(
                family="courier new",
                size=12,
                color="white"
            )), 1,3)


    fig.update_layout(height=1000)


    table_optimal_weight_fig = plotly.offline.plot(fig, auto_open = False, output_type="div")
    context['table_optimal_weight_fig'] = table_optimal_weight_fig





    fig = go.Figure()
    rets = investor.portfolio.portfolio_returns_over_time
    fig.add_trace(go.Scatter(x=list(rets.keys()), y=list(rets.values()), name='Returns', line_shape='spline', marker={'color':'black'}))

    rets_over_time = plotly.offline.plot(fig, auto_open = False, output_type="div")
    context['rets_over_time'] = rets_over_time














    return render_template('portfolio.html', **context)

@app.route('/test_graph_page')
def test_graph_page():


    return render_template('test_graph_page.html')


@app.route('/new_stock_position')
def new_stock_position():




    return render_template('new_stock_position.html')

@app.route('/new_bond_position')
def new_bond_position():




    return render_template('new_bond_position.html')

@app.route('/new_order', methods = ['GET', 'POST'])
def new_order():

    global investor

    context = dict()

    if request.method == 'POST':

        data = request.form

        if data.get('password') == investor.password:

            asset_type = data.get('asset_type')

            if asset_type == 'equity':

                ticker = data.get('ticker')
                num_shares = int(data.get('num_shares'))
                # buy_price = float(data.get('buy_price'))
                initial_datetime_str = datetime.datetime.now().strftime(DT_STRING_FORMATTER)
                # investment_sector = data.get('investment_sector')

                position = StockPosition(ticker = ticker, num_shares = num_shares, initial_datetime_str = initial_datetime_str)

                context['is_equity'] = True
                context['is_fixed_income'] = False

                context['ticker'] = ticker
                context['num_shares'] = num_shares
                buy_price = position.buy_price
                context['buy_price'] = f'{buy_price:,}'
                context['initial_datetime_str'] = initial_datetime_str

            elif asset_type == 'fixed_income':


                bond_type = data.get('bond_type')

                if bond_type == 'municipal':

                    initial_margin = float(data.get('initial_margin'))
                    initial_datetime_str = datetime.datetime.now().strftime(DT_STRING_FORMATTER)
                    maturity_date = data.get('maturity_date')
                    bond_yield = float(data.get('bond_yield'))
                    if bond_yield > 1:
                        # Making sure yield is a decimal
                        bond_yield /= 100
                    period = data.get('period')
                    rating = data.get('rating')
                    federal_tax_rate = float(data.get('federal_tax_rate'))
                    if federal_tax_rate > 1:
                        # Making sure tax rate is a decimal
                        federal_tax_rate /= 100
                    state_tax_rate = float(data.get('state_tax_rate'))
                    if state_tax_rate > 1:
                        # Making sure tax rate is a decimal
                        state_tax_rate /= 100
                    county_tax_rate = float(data.get('county_tax_rate'))
                    if county_tax_rate > 1:
                        # Making sure tax rate is a decimal
                        county_tax_rate /= 100

                    position = MunicipalBond(investor_obj = investor,
                                        initial_margin = initial_margin,
                                        initial_datetime_str = initial_datetime_str,
                                        maturity_date = maturity_date, bond_yield = bond_yield,
                                        period = period, rating = rating,
                                        bond_federal_tax_rate = federal_tax_rate,
                                        bond_state_tax_rate = state_tax_rate, bond_local_tax_rate = county_tax_rate)


                    context['is_equity'] = False
                    context['is_fixed_income'] = True

                    context['bond_type'] = bond_type
                    context['initial_margin'] = f'{initial_margin:,}'
                    context['initial_datetime_str'] = initial_datetime_str
                    context['maturity_date'] = maturity_date
                    context['bond_yield'] = bond_yield
                    context['period'] = period
                    context['rating'] = rating
                    context['federal_tax_rate'] = federal_tax_rate
                    context['state_tax_rate'] = state_tax_rate
                    context['county_tax_rate'] = county_tax_rate


                else:
                    # Different type of bond
                    pass
            else:
                # Different type of asset
                pass


            position_filled = investor.portfolio.add_position(position)

            context['position_filled'] = position_filled


            return render_template('new_order.html', **context)


        else:

            return render_template('incorrect_password.html')





    return render_template('new_order.html')

if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', debug=True)
