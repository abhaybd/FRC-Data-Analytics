"""
Basically place a team in a 2d space. 
Next team: create a gaussian prob field with relation to num_bonds
each team is likely to be placed closer to teams it has high bonds with
if no bonds, skip and come back


THIS IS PRETTY MUCH BROKEN!! WIP!
"""


import tbapy
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from keymanager import get_key

def create_team_bonds(year_low, year_high, dist_frag, tba, reload=False, save=True):
    file = '%s_bonds_%d-%d.json' % (dist_frag, year_low, year_high)
    if not reload and os.path.isfile(file):
        print('Using existing bonds')
        with open(file) as f:
            return json.loads(f.read())
    years = range(year_low, year_high)
    districts = [str(year) + dist_frag for year in years]
    
    alliances = []
    for dist in districts:
        events = tba.district_events(dist, keys=True)
        for event in events:
            alliances.extend(tba.event_alliances(event))
    
    alliances = [a['picks'] for a in alliances]
    
    teams = set(np.array(alliances).flatten())
    team_bonds = {}
    for team in teams:
        team_bonds[team] = {}
    
    for a in alliances:
        for i in range(2):
            others = list(range(3))
            others.remove(i)
            for j in others:
                if a[j] not in team_bonds[a[i]]:
                    team_bonds[a[i]][a[j]] = 0
                team_bonds[a[i]][a[j]] += 1
                if a[i] not in team_bonds[a[j]]:
                    team_bonds[a[j]][a[i]] = 0
                team_bonds[a[j]][a[i]] += 1
    if save:
        with open(file, 'w') as f:
            f.write(json.dumps(team_bonds))
    return team_bonds

def _create_2dgaussian(mean_x, mean_y, stdev, low=-10, high=10, n_samples=None):
    if n_samples is None:
        n_samples = int((high - low) / 0.02)
    x, y = np.meshgrid(np.linspace(low, high, n_samples), np.linspace(low, high, n_samples))
    d = np.hypot(x-mean_x, y-mean_y)
    g = np.exp(-(d**2 / (2.0 * stdev**2)))
    return g

def place_team(placed_teams, team_bonds, team) -> bool:
    connected_teams = [t for t in placed_teams.keys() if t in team_bonds[team]]
    if len(connected_teams) == 0:
        return False
    fields = [_create_2dgaussian(x, y, 1./team_bonds[team][t]**6, -10, 10) for t,(x,y) in placed_teams.items() if t in team_bonds[team]]
    merged_field = np.average(fields, axis=0)
    r = np.random.random() * np.sum(merged_field)
    integrand = 0
    for y in range(merged_field.shape[0]):
        for x in range(merged_field.shape[1]):
            integrand += merged_field[y,x]
            if integrand >= r:
                placed_teams[team] = ((x/merged_field.shape[1]) * 20 - 10, (y/merged_field.shape[0]) * 20 - 10)
                return True
    raise Exception('Whack shit!')

def create_map(team_bonds):
    placed_teams = {}
    teams = list(team_bonds.keys())
    placed_teams[teams[0]] = (0,0)
    teams.remove(teams[0])
    i = 0
    while len(teams) > 0:
        team = teams[i]
        if place_team(placed_teams, team_bonds, team):
            teams.remove(team)
        else:
            i += 1
        if i == len(teams) - 1:
            i = 0
    return placed_teams

tba = tbapy.TBA(get_key())
bonds = create_team_bonds(2014, 2019, 'pnw', tba)
placed = create_map(bonds)

plt.clf()
for team, (x,y) in placed.items():
    plt.scatter(x, y)
    plt.annotate(team, (x, y))
plt.show()