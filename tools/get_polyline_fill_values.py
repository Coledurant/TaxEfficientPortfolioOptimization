import numpy as np
import pandas as pd



def get_polyline_fill_values(returns_over_time_dict):

    percents = {x:y*100 for x,y in returns_over_time_dict.items()}

    min_percent = abs(min(percents.values())) + 29

    percents = {x:y + min_percent for x,y in percents.items()}


    scale_value = 75 / max(percents.values())

    percents = {x:y*scale_value for x,y in percents.items()}

    percents = pd.DataFrame(percents.values(), index=percents.keys(), columns=['percent'])
    percents.reset_index(drop=True, inplace=True)

    index_scaler = 600 / percents.index[-1]

    percents = {i:percents.iloc[i]['percent'] for i in percents.index}

    percents = {int(i*index_scaler):int(x) for i,x in percents.items()}


    return "".join(["{},{} ".format(x,75-y) for x,y in percents.items()])
