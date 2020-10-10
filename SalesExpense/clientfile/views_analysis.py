# -*- coding: utf-8 -*-
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from sheets.models import Staff
from sheets.views import build_formatters_by_col
import pandas as pd
from .charts import *
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .views_clients import get_clients, get_context_from_form, get_df_clients, D_FIELD, D_SELECT

SERIES_LIMIT = 10  # 所有画图需要限制的系列数

@login_required()
def analysis(request):
    DISPLAY_LENGTH = 20
    context = get_context_from_form(request)
    clients = get_clients(request.user, context)
    clients = sorted(clients, key=lambda p: p.monthly_patients(), reverse=True)
    paginator = Paginator(clients, DISPLAY_LENGTH)
    page = request.POST.get('page')
    try:
        rows = paginator.page(page)
    except PageNotAnInteger:
        rows = paginator.page(1)
    except EmptyPage:
        rows = paginator.page(paginator.num_pages)
    context = {
        'client_list': rows,
        'num_pages': paginator.num_pages,
        'record_n': paginator.count,
        'display_length': DISPLAY_LENGTH,
    }
    if request.is_ajax():
        return render(request, 'clientfile/client_cards.html', context)
    else:
        context['field_list'] = D_FIELD
        for key, value in context['field_list'].items():
            context['field_list'][key] = {}
            context['field_list'][key]['select'] = D_SELECT[key]
            context['field_list'][key]['options'] = get_unique(clients, value)
        return render(request, 'clientfile/analysis.html', context)


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        chart = self.kwargs.get('chart')
        return json_response(json.loads(get_chart(request, chart)))


def get_chart(request, chart):
    context = get_context_from_form(request)
    group_id = request.GET.get('group_id')
    if group_id is None:
        df = get_df_clients(request.user, context=context)
    else:
        df = get_df_clients(request.user, context=context, is_deleted=True, group_id=group_id)
    if chart == 'scatter_client':
        df['客户姓名'] = df['区域']+'_'+df['大区']+'_'+df['地区经理']+'_'+df['负责代表']+'_'+df['客户姓名']
        df = df.loc[: , ['客户姓名', '月累计相关病人数', '当前月处方量']]
        df['bubble_size'] = 1
        df.set_index(['客户姓名'], inplace=True)
        c = bubble(df, symbol_size=0.2, show_label=False)
    elif chart == 'bar_dsm':
        pivoted = pd.pivot_table(df, index='地区经理', values='客户姓名', aggfunc='count')
        pivoted.columns = ['客户档案数']
        c = bar(pivoted)
    elif chart == 'bar_dept_potential':
        df_count = df['客户姓名'].groupby(df['所在科室']).count()
        df_count = df_count.reindex(['心内科', '肾内科', '神内科', '内分泌科', '老干科', '其他科室'])
        pivoted = pd.pivot_table(df, index='所在科室', values='月累计相关病人数', aggfunc=np.mean)
        pivoted.columns = ['平均月累计相关病人数']
        pivoted = pivoted.round(1).reindex(df_count.index)
        c = bar(pivoted, show_label=True)
    elif chart == 'bar_hpaccess_potential':
        df_count = df['客户姓名'].groupby(df['是否开户']).count()
        df_count = df_count.reindex(['是', '否'])
        pivoted = pd.pivot_table(df, index='是否开户', values='月累计相关病人数', aggfunc=np.mean)
        pivoted.columns = ['平均月累计相关病人数']
        pivoted = pivoted.round(1).reindex(df_count.index)
        c = bar(pivoted, show_label=True)
    elif chart == 'bar_hplevel_potential':
        df_count = df['客户姓名'].groupby(df['医院层级']).count()
        df_count = df_count.reindex(['A', 'B', 'C', 'D', '旗舰社区', '普通社区'])
        pivoted = pd.pivot_table(df, index='医院层级', values='月累计相关病人数', aggfunc=np.mean)
        pivoted.columns = ['平均月累计相关病人数']
        pivoted = pivoted.round(1).reindex(df_count.index)
        c = bar(pivoted, show_label=True)
    elif chart == 'bar_title_potential':
        df_count = df['客户姓名'].groupby(df['职称']).count()
        df_count = df_count.reindex(['院长', '副院长', '主任医师', '副主任医师', '主治医师', '住院医师'])
        pivoted = pd.pivot_table(df, index='职称', values='月累计相关病人数', aggfunc=np.mean)
        pivoted.columns = ['平均月累计相关病人数']
        pivoted = pivoted.round(1).reindex(df_count.index)
        c = bar(pivoted, show_label=True)
    elif chart == 'pie_dept':
        df_count = df['客户姓名'].groupby(df['所在科室']).count()
        df_count = df_count.reindex(['心内科', '肾内科', '神内科', '内分泌科', '老干科', '其他科室'])
        c = pie_radius(df_count)
    elif chart == 'pie_hpaccess':
        df_count = df['客户姓名'].groupby(df['是否开户']).count()
        df_count = df_count.reindex(['是', '否'])
        c = pie_radius(df_count)
    elif chart == 'pie_hplevel':
        df_count = df['客户姓名'].groupby(df['医院层级']).count()
        df_count = df_count.reindex(['A', 'B', 'C', 'D', '旗舰社区', '普通社区'])
        c = pie_radius(df_count)
    elif chart == 'pie_title':
        df_count = df['客户姓名'].groupby(df['职称']).count()
        df_count = df_count.reindex(['院长', '副院长', '主任医师', '副主任医师', '主治医师', '住院医师'])
        c = pie_radius(df_count)
    elif chart == 'pie_potential_level':
        df_count = df['客户姓名'].groupby(df['潜力级别']).count()
        df_count = df_count.reindex(['H', 'M', 'L'])
        c = pie_radius(df_count)
    elif chart == 'bar_line_potential_dist':
        df['潜力区间'] = pd.cut(df['月累计相关病人数'], 20).astype(str)
        df_count = df['潜力区间'].groupby(df['潜力区间']).count()
        df_sorted = df_count[sorted(df_count.index, key=lambda x: float(x.split(", ")[0][1:]))].to_frame()
        c = bar(df_sorted, show_label=True, label_rotate=30)
    elif chart == 'treemap_rsp_hosp_client':
        pivoted = pd.pivot_table(df, index=['负责代表', '医院全称', '客户姓名'], values='月累计相关病人数', aggfunc=sum)
        df = pivoted.reset_index()

        list_rsp = [{'value': sum(v.tolist()), 'name': k } for k, v in df.groupby("负责代表")["月累计相关病人数"]]
        for rsp in list_rsp:
            df2 = df[df['负责代表'] == rsp['name']]
            list_hosp = [{'value': sum(v.tolist()), 'name': k } for k, v in df2.groupby("医院全称")["月累计相关病人数"]]
            rsp['children'] = list_hosp
            for hosp in list_hosp:
                df3 = df[(df['负责代表'] == rsp['name'])&(df['医院全称'] == hosp['name'])]
                list_client = [{'value': sum(v.tolist()), 'name': k} for k, v in df3.groupby("客户姓名")["月累计相关病人数"]]
                hosp['children'] = list_client

        c = treemap(list_rsp, str(request.user))
    return c.dump_options()


def ajax_table(request, index):
    context = get_context_from_form(request)
    df = get_df_clients(request.user, context)
    df_client_n = pd.pivot_table(df, index=index, values='客户姓名', aggfunc='count')
    df_client_n_cv = client_count(df, '所在科室', '心内科', index)
    df_client_n_np = client_count(df, '所在科室', '肾内科', index)
    df_client_n_noaccess = client_count(df, '是否开户', '是', index)
    df_client_n_a = client_count(df, '医院层级', 'A', index)
    df_client_n_b = client_count(df, '医院层级', 'B', index)
    df_client_n_c = client_count(df, '医院层级', 'C', index)
    df_client_n_d = client_count(df, '医院层级', 'D', index)
    df_client_n_fc = client_count(df, '医院层级', '旗舰社区', index)
    df_client_n_gc = client_count(df, '医院层级', '普通社区', index)
    df_hosp_n = pd.pivot_table(df, index=index, values='医院全称', aggfunc=lambda x: len(x.unique()))
    df_monthly_patients = pd.pivot_table(df, index=index, values='月累计相关病人数', aggfunc=np.mean)
    df_combined = pd.concat([df_client_n,
                             df_client_n_cv,
                             df_client_n_np,
                             df_client_n_noaccess,
                             df_client_n_a,
                             df_client_n_b,
                             df_client_n_c,
                             df_client_n_d,
                             df_client_n_fc,
                             df_client_n_gc,
                             df_monthly_patients,
                             df_hosp_n,
                             ], axis=1)

    df_combined.columns = ['客户档案数',
                           '心内%',
                           '肾内%',
                           '开户医院%',
                           'A级医院%',
                           'B级医院%',
                           'C级医院%',
                           'D级医院%',
                           '旗舰社区%',
                           '普通社区%',
                           '平均相关病人数',
                           '医院数',
                           ]

    for col in df_combined.columns:
        if col not in['客户档案数',  '平均相关病人数', '医院数']:
            df_combined[col] = df_combined[col]/df_combined['客户档案数']
    df_combined['客户数/医院'] = df_combined['客户档案数']/df_combined['医院数']
    df_combined.fillna(0, inplace=True)
    table = df_combined.to_html(formatters=build_formatters_by_col(df_combined), classes='ui celled table',
                                   table_id=context['table_id'], escape=False)
    return HttpResponse(table)


def get_unique(qs, field):
    unique_list = []
    for query in qs:
        str = getattr(query, field)
        if str is True:
            str = "是"
        elif str is False:
            str = "否"
        if str not in unique_list:
            unique_list.append(str)
    return unique_list


def client_count(df, column, target, index):
    if df[df[column] == target].shape[0] > 0:
        df_client_n = pd.pivot_table(df, index=index, columns=column, values='客户姓名', aggfunc=len).loc[:, target]
    else:
        df_client_n = pd.pivot_table(df, index=index, columns=column, values='客户姓名', aggfunc=len)
        df_client_n[target] = 0
        df_client_n = df_client_n.loc[:, target]
    return df_client_n