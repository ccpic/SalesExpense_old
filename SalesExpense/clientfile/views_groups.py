# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
import pandas as pd
from .views_clients import get_clients
from .models import Group, Client
from django.views.decorators.http import require_http_methods
from .views_clients import get_clients, get_df_clients
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import scipy.stats as stats
from django.db.models import Q

@login_required()
def groups(request):
    groups = Group.objects.filter(created_by=request.user)
    clients = get_clients(request.user)
    context = {
        'groups': groups,
        'clients': clients
    }
    return render(request, 'clientfile/groups.html', context)


@login_required()
def group_detail(request, id):
    group = Group.objects.get(id=id)

    DISPLAY_LENGTH = 20
    clients = group.clients_all_with_deleted()
    clients = sorted(clients, key=lambda p: p.monthly_patients(), reverse=True)
    paginator = Paginator(clients, DISPLAY_LENGTH)
    page = request.POST.get('page')
    try:
        rows = paginator.page(page)
    except PageNotAnInteger:
        rows = paginator.page(1)
    except EmptyPage:
        rows = paginator.page(paginator.num_pages)

    '''计算平均潜力在名下档案中的百分位排名'''
    clients_all = get_clients(request.user)
    list_potential = []
    for client in clients_all:
        list_potential.append(client.monthly_patients())
    pct_rank = '{:.1%}'.format(stats.percentileofscore(list_potential, group.avg_monthly_patients())/100)

    context = {
        'group': group,
        'client_list': rows,
        'num_pages': paginator.num_pages,
        'record_n': paginator.count,
        'display_length': DISPLAY_LENGTH,
        'potential_rank': pct_rank
    }

    return render(request, 'clientfile/group_detail.html', context)


@login_required()
@require_http_methods('POST')
def add_group(request):
    if request.method == 'POST':
        created_by = request.user
        name = request.POST.get('name')
        note = request.POST.get('note')
        # viewable_users_list = request.POST.getlist('users-select[]')
        # viewable_users_obj_list = User.objects.filter(id__in=viewable_users_list) # 查找Auth User表对应id的多个obj
        clients_list = request.POST.getlist('clients-select[]')
        clients_obj_list = Client.objects.filter(id__in=clients_list)  # 查找Client表对应id的多个obj

        group = Group.objects.create(created_by=created_by, name=name, note=note)
        # group.clients.add(*viewable_users_obj_list)
        group.clients.add(*clients_obj_list)
        group.save()
        return redirect(reverse('clientfile:groups'))


@login_required()
@require_http_methods('POST')
def delete_group(request):
    if request.method == "POST":
        id = request.POST.get('id')
        qs_to_delete = Group.objects.filter(id=id)  # 执行删除操作
        qs_to_delete.delete()
        return redirect(reverse('clientfile:groups'))
