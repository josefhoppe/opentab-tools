from opentab_api import *
from jinja2 import Environment, FileSystemLoader

import random, os
import xml.dom.minidom

import numpy as np

def shuffled(l: list) -> list:
    random.shuffle(l)
    return l

def question_explanation(question: dict):
    if not 'parameters' in question:
        return ''
    params = question['parameters']
    if not 'labels' in params:
        return ''
    labels = params['labels']
    return ', '.join([ f'{k}: {v}' for k,v in labels.items()])

def format_feedback_tc(judge: str, df_feedback: pd.DataFrame, jinja_env: Environment):
    numerics = [ {
        'title': 'Score',
        'explanation': 'Numerische Gesamtwertung, gemittelt von Chairs, Wings, und Teams',
        'mean': df_feedback['score'].mean()
    } ]

    others = [ {
        'title': 'Feedback',
        'contents': [ s for s in shuffled(df_feedback['answer'].to_list()) if s != '' ]
    } ]

    template = jinja_env.get_template("feedback.html")
    return template.render(name=judge, numerics=numerics, others=others)

def format_feedback(questions: List[dict], feedback: JudgeFeedback, jinja_env: Environment):
    numerics = [ {
        'title': q['description'],
        'explanation': question_explanation(q),
        'mean': feedback.values[q['name']].mean()
    } for q in questions if q['type'] == 'discrete']

    numerics = [ n for n in numerics if not np.isnan(n['mean']) ]

    others = [ {
        'title': q['description'],
        'contents': [ s for s in shuffled(feedback.values[q['name']].to_list()) if s != '' ]
    } for q in questions if q['type'] != 'discrete']

    template = jinja_env.get_template("feedback.html")
    return template.render(name=feedback.name, numerics=numerics, others=others)

def output_all_feedback(target_folder = 'feedback/'):
    environment = Environment(loader=FileSystemLoader("templates/"), autoescape=True)
    feedback = get_all_feedback()
    os.makedirs(target_folder, exist_ok=True)
    for judge in feedback.feedback:
        res = format_feedback(feedback.questions, judge, environment)
        with open(f'{target_folder}{judge.token}.html', mode="w", encoding="utf-8") as fb_file:
            fb_file.write(res)

def output_all_feedback_tabbycat(target_folder = 'feedback/'):
    environment = Environment(loader=FileSystemLoader("templates/"), autoescape=True)
    df_feedback = pd.read_csv('feedback.csv')
    df_judges = pd.read_csv('tablinks.csv', index_col=0)
    print(df_judges)
    os.makedirs(target_folder, exist_ok=True)
    for judge in df_feedback.to.unique():
        res = format_feedback_tc(judge, df_feedback[df_feedback.to == judge], environment)
        with open(f'{target_folder}{df_judges.loc[judge]["url"]}.html', mode="w", encoding="utf-8") as fb_file:
            fb_file.write(res)