# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pandas as pd
from .views_clients import get_clients
from datetime import datetime, timedelta
from .models import Group, Client

@login_required()
def history(request):
    clients_his = get_clients(request.user, is_deleted=True)
    clients_his_n = len(clients_his)
    one_week_ago = datetime.today() - timedelta(days=7)
    clients_his_latest_week = clients_his.filter(pub_date__gte=one_week_ago)
    clients_his_latest_week_n= len(clients_his_latest_week)
    if clients_his_latest_week_n > 0:
        df = pd.DataFrame(list(clients_his.values('name', 'pub_date', 'is_deleted', 'dsm')))
        df.dropna(inplace=True)
        df['modifier'] = df['pub_date'].dt.strftime('%Y-%m-%d %H:%M') + '|' + df['is_deleted'].astype(str) + '|' + df['dsm']
        pivoted = pd.pivot_table(data=df, values='name', index='modifier', aggfunc='count')

        d_clients_his = pivoted.to_dict()['name']
        d_clients_his_inv = {}
        for k, v in d_clients_his.items():
            dict_element = {k: v}
            dict_element.update(d_clients_his_inv)
            d_clients_his_inv = dict_element
    else:
        d_clients_his_inv = {}


    groups_his = Group.objects.all()
    groups_his_n = groups_his.count()
    groups_his_latest_week = groups_his.filter(pub_date__gte=one_week_ago).order_by('-pub_date')
    groups_his_latest_week_n = groups_his_latest_week.count()

    context = {
        'clients_his_latest_week': d_clients_his_inv,
        'clients_his_latest_week_n': clients_his_latest_week_n,
        'clients_his_n': clients_his_n,
        'groups_his_latest_week': groups_his_latest_week,
        'groups_his_latest_week_n': groups_his_latest_week_n,
        'groups_his_n': groups_his_n
    }
    return render(request, 'clientfile/history.html', context)
