# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
import pandas as pd
from .views_clients import get_clients
from .models import Group, Client
from django.views.decorators.http import require_http_methods

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
@require_http_methods('POST')
def add_group(request):
    if request.method == 'POST':
        created_by = request.user
        name = request.POST.get('name')
        note = request.POST.get('note')
        clients_list = request.POST.getlist('clients-select[]')
        print(clients_list)
        clients_obj_list = Client.objects.filter(id__in=clients_list)  # 查找Author表对应id的多个obj

        group = Group.objects.create(created_by=created_by, name=name, note=note)
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
