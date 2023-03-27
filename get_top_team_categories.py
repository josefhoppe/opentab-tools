"""
retrieves points from opentab, aggregates team points by team, and prints the result to the console.
"""

import pandas as pd
from opentab_api import get_team_results
df_team_res = get_team_results()

agg = {'team_name': 'first', 'team_points': 'sum'}
df_top_teams = df_team_res.groupby('team_id').agg(agg).sort_values('team_points', ascending=False)

print(df_top_teams)