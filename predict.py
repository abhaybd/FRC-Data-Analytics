from opr_calc import district_oprs
from rpr_calc import district_rprs
import tbapy
import numpy as np
from keymanager import get_key

def predict_event_matches(event, oprs, tba):
    matches = tba.event_matches(event)
    correct = 0
    preds = []
    for match in matches:
        winner = predict_match(match, oprs)
        correct += winner == match['winning_alliance']
        preds.append(winner)
    print(correct / len(matches))
    return preds

def predict_match(match, oprs):
    avg_opr = np.mean(list(oprs.values()))
    red_teams = match['alliances']['red']['team_keys']
    red_pred = sum(oprs[team] if team in oprs else avg_opr for team in red_teams)
    blue_teams = match['alliances']['blue']['team_keys']
    blue_pred = sum(oprs[team] if team in oprs else avg_opr for team in blue_teams)
    winner = 'red' if red_pred >= blue_pred else 'blue'
    return winner

def predict_match_rp(match, oprs, rprs=None):
    rp = {'blue':0, 'red':0}
    rp[predict_match(match,oprs)] += 2
    if rprs is not None:
        avg_rpr = np.mean(list(rprs.values()))    
        red_teams = match['alliances']['red']['team_keys']
        rp['red'] += max(int(sum(rprs[team] if team in rprs else avg_rpr for team in red_teams)), 0)
        blue_teams = match['alliances']['blue']['team_keys']
        rp['blue'] += max(int(sum(rprs[team] if team in rprs else avg_rpr for team in blue_teams)), 0)
    return rp

def predict_event_rankings(event, oprs, tba, rprs=None):
    matches = tba.event_matches(event)
    teams = tba.event_teams(event, keys=True)
    ranking_points = {team:0 for team in teams}
    
    for i, match in enumerate(matches):
        rp = predict_match_rp(match, oprs, rprs)
        for team in match['alliances']['red']['team_keys']:
            ranking_points[team] += rp['red']
        for team in match['alliances']['blue']['team_keys']:
            ranking_points[team] += rp['blue']
    rankings = [item[0] for item in sorted(list(ranking_points.items()), reverse=True, key=lambda x: x[1])]
    return rankings

def _emd(rankings, real_rankings):
    total = 0
    for i,team in enumerate(rankings):
        real_index = real_rankings.index(team)
        total += abs(real_index - i)
    return total

if __name__ == '__main__':
    tba = tbapy.TBA(get_key())
    event = '2019pncmp'
    district = '2019pnw'
    oprs = district_oprs(district, tba, exclusions=[event])
    rprs = district_rprs(district, tba, exclusions=[event])
    rankings = predict_event_rankings(event, oprs, tba, rprs)
    real_rankings = [rank['team_key'] for rank in tba.event_rankings(event)['rankings']]
    cost = _emd(rankings, real_rankings)
    print('Predicted rankings with cost: %d' % cost)
    print('Top 8 similarity: %d/8' % (16 - len(set(rankings[:8] + real_rankings[:8]))))