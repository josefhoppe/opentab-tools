

import pandas as pd
import requests
import itertools
from typing import NamedTuple, Dict, List, Tuple

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

def get_feedback_table(base_url=BASE_URL) -> pd.DataFrame:
    feedback = requests.get(base_url + '/tournament/1/feedback').json()
    df_outer = pd.DataFrame(feedback['responses'])
    df_inner = pd.DataFrame(df_outer['answers'].to_list())
    df_all = pd.concat([df_outer.drop('answers', axis='columns'), df_inner],axis='columns')
    return df_all

def get_all_feedback(base_url=BASE_URL) -> Feedback:
    judges = requests.get(base_url + '/tournament/1/judges').json()['payload']
    judge_map = { judge['href']: JudgeFeedback(judge['fullName'], judge['href']) for judge in judges }

    feedback = requests.get(base_url + '/tournament/1/feedback').json()
        
    df_all = get_feedback_table(base_url)

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

def should_have_submitted_feedback(base_url=BASE_URL, round='r/1') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    calculates for the given round, what feedback should have been given to whom
    and which participant counts for which feedback (themselves or team)

    returns (should_submit, counts_as, display_names)
    """
    draw = requests.get(f'{BASE_URL}/{round}/draw').json()['payload']
    res = []
    counts_res = []

    for room in draw['draw']['rooms']:
        chair = room['judges'][0]['href']
        counts_res.append({'person': chair, 'feedbacker': chair})
        for fs in room['freeSpeakers']:
            res.append({'from': fs['href'], 'to': chair})
            counts_res.append({'person': fs['href'], 'feedbacker': fs['href']})
        for wing in room['judges'][1:]:
            res.append({'from': wing['href'], 'to': chair})
            res.append({'to': wing['href'], 'from': chair})
            counts_res.append({'person': wing['href'], 'feedbacker': wing['href']})
        res.append({'from': room['government']['href'], 'to': chair})
        for speaker in draw['entities'][room['government']['href']]['members']:
            counts_res.append({'person': speaker, 'feedbacker': room['government']['href']})
        res.append({'from': room['opposition']['href'], 'to': chair})
        for speaker in draw['entities'][room['opposition']['href']]['members']:
            counts_res.append({'person': speaker, 'feedbacker': room['opposition']['href']})

    df_names = pd.DataFrame([{'href': key, 'name': entity['displayName']} for key, entity in draw['entities'].items()]).set_index('href')

    return pd.DataFrame(res), pd.DataFrame(counts_res), df_names