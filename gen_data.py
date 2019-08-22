import pandas as pd
import os
import tbapy
from keymanager import get_key

tba = tbapy.TBA(get_key())

def scrape_event(event, dir_name='event_matches', save=True):
    matches = tba.event_matches(event)
    data = []
    for match in matches:
        red_won = match['winning_alliance'] == 'red'
        red = match['alliances']['red']['team_keys']
        blue = match['alliances']['blue']['team_keys']
        red_score = match['alliances']['red']['score']
        blue_score = match['alliances']['blue']['score']
        data += [[int(red_won)] + red + blue + [red_score, blue_score]]
    df = pd.DataFrame(data)
    df.columns = ['red_won', 'red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3', 'red_score', 'blue_score']
    if save:
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        df.to_csv(os.path.join(dir_name, '%s.csv' % event))
    return df

def event_oprs(event, dir_name='event_oprs', save=True):
    oprs = pd.DataFrame(tba.event_oprs(event))
    if save:
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        oprs.to_csv(os.path.join(dir_name, '%s.csv' % event))
    return oprs

def check_preds(event, df):
    oprs = event_oprs(event)
    correct = 0
    for i, row in df.iterrows():
        red = sum([oprs['oprs'][row[col]] for col in ['red1', 'red2', 'red3']])
        blue = sum([oprs['oprs'][row[col]] for col in ['blue1', 'blue2', 'blue3']])
        correct += bool(red > blue) == row['red_won']
    print(correct / df.shape[0])

if __name__ == '__main__':
    event_name = '2019wasno' # input('What event to scrape? ')
    df = scrape_event(event_name)
    check_preds(event_name, df)