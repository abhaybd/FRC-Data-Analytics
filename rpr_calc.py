import numpy as np
from scipy import sparse
import os
import tbapy
import json
from keymanager import get_key

def district_rprs(district, tba, exclusions=[], force_reload=False, save=True):
    if not force_reload and os.path.isfile('%s_rprs.json' % district):
        print('Using cached rprs')
        with open('%s_rprs.json' % district) as f:
            oprs = json.loads(f.read())
            return oprs
    matches = []
    events = tba.district_events(district, keys=True)
    events = [e for e in events if e not in exclusions]
    for event in events:
        matches += tba.event_matches(event)
    rprs = calc_rprs(matches)
    if save:
        with open('%s_rprs.json' % district, 'w') as f:
            f.write(json.dumps(rprs))
    return rprs

def calc_rprs(matches):
    teams = _get_teams_from_matches(matches)
    match_matrix = sparse.lil_matrix((2*len(matches), len(teams)))
    rp_matrix = np.empty([2*len(matches), 1])
    i = 0
    for match in matches:
        red_teams = match['alliances']['red']['team_keys']
        red_rps = match['score_breakdown']['red']['rp']
        for team in red_teams:
            match_matrix[i,teams.index(team)] = 1
        rp_matrix[i,0] = red_rps
        i += 1
        blue_teams = match['alliances']['blue']['team_keys']
        blue_rps = match['score_breakdown']['blue']['rp']
        for team in blue_teams:
            match_matrix[i,teams.index(team)] = 1
        rp_matrix[i,0] = blue_rps
        i += 1
    
    T = match_matrix.transpose()
    a = T @ match_matrix
    b = T @ rp_matrix
    oprs = sparse.linalg.spsolve(a, b.flatten())
    return {teams[i]:oprs[i] for i in range(len(teams))}

def _get_teams_from_matches(matches):
    teams = []
    for match in matches:
        teams += match['alliances']['red']['team_keys']
        teams += match['alliances']['blue']['team_keys']
    return sorted(list(set(teams)), key=lambda x: int(x[3:]))

if __name__ == '__main__':
    tba = tbapy.TBA(get_key())
    event = '2019wasno'
    matches = tba.event_matches(event)
    rprs = calc_rprs(matches)
    all_rprs = district_rprs('2019pnw', tba)