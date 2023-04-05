"""
different reports aggregated from opentab
"""

from opentab_api import *

def feedback_shame_table(base_url = BASE_URL, round = 'r/1') -> pd.DataFrame:
    """
    Table of all teams and individuals that still need to submit feedback for adjudicators
    """
    df_should_submit, df_submits_for, df_names = should_have_submitted_feedback(base_url, round)
    df_feedback = get_feedback_table(base_url)

    df_should_submit['count'] = 1
    df_feedback_given = df_feedback.set_index('source').loc[:,['round_number', 'target']].join(df_submits_for.set_index('person')).reset_index().rename(columns={'feedbacker': 'from', 'target': 'to'}).set_index(['from', 'to'])
    df_submit_compare = df_should_submit.set_index(['from', 'to']).join(df_feedback_given).groupby('from').agg({'count': 'sum', 'index': 'count'}).rename(columns={'count': 'should', 'index': 'given'})

    df_shame = df_submit_compare[df_submit_compare.given < df_submit_compare.should].join(df_names)
    df_shame['missing'] = df_shame.should - df_shame.given

    return df_shame.sort_values('missing', ascending=False)