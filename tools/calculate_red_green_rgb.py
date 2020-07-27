


def calculate_red_green_rgb(investment_return):

    rgb_value = abs(int(investment_return * 255))

    if investment_return < 0:
        rgb_statement = 'RGB({},0,0)'.format(rgb_value)
    elif investment_return > 0:
        rgb_statement = 'RGB(0,{},0)'.format(rgb_value)
    else:
        rgb_statement = 'RGB(0,0,0)'

    return rgb_statement
