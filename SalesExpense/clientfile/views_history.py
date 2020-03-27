# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pandas as pd
from .views_clients import get_clients

@login_required()
def history(request):
    history = get_clients(request.user, is_deleted=True)
    history_n = len(history)
    df = pd.DataFrame(list(history.values('name', 'pub_date', 'is_deleted', 'dsm')))
    df.dropna(inplace=True)
    df['modifier'] = df['pub_date'].dt.strftime('%Y-%m-%d %H:%M') + '|' + df['is_deleted'].astype(str) + '|' + df['dsm']
    pivoted = pd.pivot_table(data=df, values='name', index='modifier', aggfunc='count')

    d_history = pivoted.to_dict()['name']
    d_history_inv = {}
    for k, v in d_history.items():
        dict_element = {k: v}
        dict_element.update(d_history_inv)
        d_history_inv = dict_element

    context = {
        'history': d_history_inv,
        'history_n': history_n
    }
    return render(request, 'clientfile/history.html', context)
