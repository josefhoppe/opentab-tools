from opentab_api import *
from jinja2 import Environment, FileSystemLoader

import random, os

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