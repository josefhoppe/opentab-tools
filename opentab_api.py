

import pandas as pd
import requests
import itertools
from typing import NamedTuple, Dict, List

BASE_URL = 'http://localhost:5000'

class JudgeFeedback:
    name: str
    ref: str
    token: str
    values: pd.DataFrame

    def __init__(self, name = "", ref = "", token = ""):
        self.name = name
        self.ref = ref
        self.token = token

class Feedback(NamedTuple):
    questions: List[dict]
    feedback: List[JudgeFeedback]

def get_all_feedback(base_url=BASE_URL) -> Feedback:
    judges = requests.get(base_url + '/tournament/1/judges').json()['payload']
    judge_map = { judge['href']: JudgeFeedback(judge['fullName'], judge['href']) for judge in judges }
        
    feedback = requests.get(base_url + '/tournament/1/feedback').json()
    df_outer = pd.DataFrame(feedback['responses'])
    df_inner = pd.DataFrame(df_outer['answers'].to_list())
    df_all = pd.concat([df_outer.drop('answers', axis='columns'), df_inner],axis='columns')

    remote_status = requests.get(base_url + '/tournament/1/remote-status').json()['payload']['debatersRemoteStatus']
    for status in remote_status:
        ref = status['participantHref']
        if ref in judge_map:
            link = status['registrationLink']
            judge_map[ref].token = link.split('/')[-1]
            judge_map[ref].values = df_all[df_all.target == ref]


    return Feedback(feedback['questions'], list(judge_map.values()))

def get_all_tablinks(base_url=BASE_URL) -> pd.DataFrame:
    df_judges = pd.DataFrame(requests.get(base_url + '/tournament/1/judges').json()['payload']).set_index('debater').loc[:,['firstName']]
    df_speakers = pd.DataFrame(requests.get(base_url + '/tournament/1/teams').json()['payload']['speakers']).set_index('debater').loc[:,['firstName']]
    df_tablinks = pd.DataFrame(requests.get(base_url + '/tournament/1/remote-status').json()['payload']['debatersRemoteStatus']).set_index('debaterHref')
    df_tablinks = df_tablinks.join(pd.concat((df_judges,df_speakers))).loc[:,['firstName', 'name', 'email','registrationLink']]
    return df_tablinks

def get_team_results(base_url=BASE_URL) -> pd.DataFrame:
    """
    Retrieves a DataFrame of all team score results
    """
    rounds = [ r['href'] for r in requests.get(base_url + '/tournament/1/rounds').json() ]
    res = []
    for r in rounds:
        rooms = requests.get(base_url + '/' + r).json()['payload']['rooms']
        for room in rooms:
            res.append({
                'round': r,
                'debate_id': room['href'],
                'room_id': room['venue']['href'],
                'room_name': room['venue']['name'],
                'team_id': room['government']['href'],
                'team_name': room['government']['name'],
                'team_pos': 'gov',
                'team_points': room['totalGovernmentTeamScore'],
                'total_points': room['totalGovernmentScore']
            })
            res.append({
                'round': r,
                'debate_id': room['href'],
                'room_id': room['venue']['href'],
                'room_name': room['venue']['name'],
                'team_id': room['opposition']['href'],
                'team_name': room['opposition']['name'],
                'team_pos': 'opp',
                'team_points': room['totalOppositionTeamScore'],
                'total_points': room['totalOppositionScore']
            })
    return pd.DataFrame(res)