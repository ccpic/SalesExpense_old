# -*- coding: utf-8 -*-
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from .models import *
from sheets.models import Staff
from sheets.views import build_formatters_by_col
from django.http import HttpResponse, JsonResponse
import xlrd
import pandas as pd
import numpy as np
import datetime
from .charts import *
import json
import re
from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, CanConvertValidation, \
    MatchesPatternValidation, InRangeValidation, InListValidation, CustomElementValidation, IsDistinctValidation

try:
    from io import BytesIO as IO  # for modern python
except ImportError:
    from io import StringIO as IO  # for legacy python

pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 5000)

SERIES_LIMIT = 10  # 所有画图需要限制的系列数

D_MAP = {
    "已开户": True,
    "未开户": False,
    "是": True,
    "否": False,
    True: "是",
    False: "否",
}

D_TRANSLATE = {
    'nan': '',
    'row': '行',
    'column': '列',
    'contains trailing whitespace': '末尾含有空白字符',
    'contains leading whitespace': '起始含有空白字符',
    'is not in the list of legal options': '不在下列合法选项中',
    'does not match the pattern "^[H]{1}(\d){9}$"': '格式不符合"字母H开头跟随9位数字"',
    'contains values that are not unique': '含有和该列其他单元格重复的数据',
    'cannot be converted to type': '必须为整数',
    'was not in the range': '超出了该字段允许的范围',
}

COL = [
    '区域',
    '大区',
    '地区经理',
    '负责代表',
    '医院编码',
    '医院全称',
    '省/自治区/直辖市',
    '是否双call',
    '医院级别',
    '开户进展',
    '客户姓名',
    '所在科室',
    '职称',
    '月出诊次数（半天计）',
    '每半天\n门诊量',
    '相关病人\n比例(%)\n建议比例：40%-80%',
    '备注'
]

COL_REINDEX = [
    '区域',
    '大区',
    '地区经理',
    '负责代表',
    '医院编码',
    '医院全称',
    '省/自治区/直辖市',
    '是否双call',
    '医院层级',
    '是否开户',
    '客户姓名',
    '所在科室',
    '职称',
    '月出诊次数（半天计）',
    '每半天门诊量',
    '相关病人比例(%)',
    '备注',
    '月累计相关病人数',
    '潜力级别',
]

class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        chart = self.kwargs.get('chart')
        return json_response(json.loads(get_chart(request, chart)))


def get_chart(request, chart):
    df = get_df_clients(request.user)
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
    df = get_df_clients(request.user)
    table_id =request.GET['table_id']

    df_client_n = pd.pivot_table(df, index=index, values='客户姓名', aggfunc='count')
    df_client_n_cv= pd.pivot_table(df, index=index, columns='所在科室', values='客户姓名', aggfunc=len).loc[:, '心内科']
    df_client_n_noaccess= pd.pivot_table(df, index=index, columns='是否开户', values='客户姓名', aggfunc=len).loc[:, '是']
    df_hosp_n = pd.pivot_table(df, index=index, values='医院全称', aggfunc=lambda x: len(x.unique()))
    df_monthly_patients = pd.pivot_table(df, index=index, values='月累计相关病人数', aggfunc=np.mean)
    df_combined = pd.concat([df_client_n,
                             df_client_n_cv,
                             df_client_n_noaccess,
                             df_monthly_patients,
                             df_hosp_n,
                             ], axis=1)

    df_combined.columns = ['客户档案数',
                           '心内档案比例',
                           '开户医院档案比例',
                           '平均月累积相关病人数',
                           '医院数',
                           ]

    df_combined['心内档案比例'] = df_combined['心内档案比例']/df_combined['客户档案数']
    df_combined['开户医院档案比例'] = df_combined['开户医院档案比例']/df_combined['客户档案数']
    df_combined['客户数/医院'] = df_combined['客户档案数']/df_combined['医院数']

    table = df_combined.to_html(formatters=build_formatters_by_col(df_combined), classes='ui celled table',
                                   table_id=table_id, escape=False)
    return HttpResponse(table)


@login_required()
def clients(request):
    df = get_df_clients(request.user)
    clients = df_to_table(df, ['医院编码', '是否双call'])
    record_n = df.shape[0]
    context = {
        'table': clients,
        'record_n': record_n,
    }
    return render(request, 'clientfile/clients.html', context)


@login_required()
def export_clients(request):
    df = get_df_clients(request.user)
    excel_file = IO()

    xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')

    df.to_excel(xlwriter, 'data', index=False)

    xlwriter.save()
    xlwriter.close()

    excel_file.seek(0)

    # 设置浏览器mime类型
    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # 设置文件名
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    response['Content-Disposition'] = 'attachment; filename=' + now + '.xlsx'
    return response


@login_required()
def import_excel(request):
    SHEET_NAME = '客户档案'
    context = {'code': 0,
               'data': [],
               'recourd_n': 0,
               'msg': ''
               }
    if request.method == 'POST':
        excel_file = request.FILES.get('attachmentName')
        if excel_file is None:  # 检查没有选择本地文件就直接点击上传的错误
            context['msg'] = '没有选择本地文件'
            return JsonResponse(context)
        else:
            try:
                df = pd.read_excel(excel_file, sheet_name=SHEET_NAME)  # 检查目标工作表不存在错误
            except xlrd.biffh.XLRDError as e:
                if 'No sheet' in e.args[0]:
                    context['msg'] = '上传Excel没有名为"' + SHEET_NAME + '"的工作表'
                else:
                    context['msg'] = '读取Excel文件错误'
                return JsonResponse(context)
            else:
                if set(COL).issubset(df.columns) is False:  # 检查读取工作表表头时字段名不匹配错误
                    column_diff = set(COL) - set(list(df.columns.values))  # 缺少的字段列表
                    context['msg'] = '缺少以下必须字段，请检查' + str(column_diff)
                    return JsonResponse(context)
                else:
                    if dsm_auth(request.user, df['地区经理'].unique())[0] is False:  # 权限检查，只能上传自己/下属dsm的数据
                        context['msg'] = '权限错误，只能上传自己/下属dsm的数据，你没有权限上传下列dsm的数据' + \
                                         str(dsm_auth(request.user, df[COL[2]].unique())[1])
                        return JsonResponse(context)
                    else:
                        d_error = validate(df)
                        if d_error:
                            for key, value in d_error.items():
                                context['msg'] += key+d_error[key]
                            return JsonResponse(context)
                        else:
                            import_record(df)
                            context['code'] = 1
                            context['msg'] = '上传成功'
                            context['data'] = df_to_table(get_df_clients(request.user), ['医院编码', '是否双call'])
                            context['record_n'] = df.shape[0]
                            return JsonResponse(context)

@login_required()
def analysis(request):
    if request.user.is_staff:
        clients = Client.objects.all()
    else:
        staffs = Staff.objects.get(name=request.user).get_descendants(include_self=True)
        staff_list = [i.name for i in staffs]

        clients = Client.objects.filter(rd__in=staff_list) | Client.objects.filter(
            rm__in=staff_list) | Client.objects.filter(dsm__in=staff_list)
    clients = sorted (clients, key=lambda p: p.monthly_patients(), reverse=True)
    context = {
        'client_list': clients
    }
    return render(request, 'clientfile/analysis.html', context)


def validate(df):
    d_error = {}
    list_dept = [x[0] for x in DEPT_CHOICES]
    list_hplevel =  [x[0] for x in HPLEVEL_CHOICES]
    list_province = [x[0] for x in PROVINCE_CHOICES]
    list_title = [x[0] for x in TITLE_CHOICES]

    NullValidation = CustomElementValidation(lambda d: d is not np.nan, '该字段不能为空')
    schema = Schema([
        Column('区域', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
        Column('大区', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
        Column('地区经理', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
        Column('负责代表', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
        Column('医院编码', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation, MatchesPatternValidation(r'^[H]{1}(\d){9}$')]),
        Column('医院全称', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
        Column('省/自治区/直辖市',[InListValidation(list_province)]),
        Column('是否双call', [InListValidation(['是', '否'])]),
        Column('医院级别', [InListValidation(list_hplevel)]),
        Column('开户进展', [InListValidation(['已开户', '未开户'])]),
        Column('客户姓名', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), IsDistinctValidation()]),
        Column('所在科室', [InListValidation(list_dept)]),
        Column('职称', [InListValidation(list_title)]),
        Column('月出诊次数（半天计）', [CanConvertValidation(int), InRangeValidation(0, 62)]),
        Column('每半天\n门诊量', [CanConvertValidation(int), InRangeValidation(0, )]),
        Column('相关病人\n比例(%)\n建议比例：40%-80%', [CanConvertValidation(int), InRangeValidation(0, 100)]),
        Column('备注')
    ])
    errors = schema.validate(df.loc[:, COL])
    for error in errors:
        str_warning = str(error)
        for term in D_TRANSLATE:
            str_warning = str_warning.replace(term, D_TRANSLATE[term])
            findword = r': [0-9]\d*'
            str_warning = re.sub(findword, row_refined,str_warning)
        d_error[str_warning] = '<br>'

    d_error = {**d_error, **check_inconsist(df, '医院编码', '医院全称', 'both')}
    d_error = {**d_error, **check_inconsist(df, '区域', '大区', 'right')}
    d_error = {**d_error, **check_inconsist(df, '大区', '地区经理', 'right')}
    d_error = {**d_error, **check_inconsist(df, '地区经理', '负责代表', 'right')}
    d_error = {**d_error, **check_inconsist(df, '医院编码', '省/自治区/直辖市', 'left')}
    d_error = {**d_error, **check_inconsist(df, '医院编码', '是否双call', 'left')}
    d_error = {**d_error, **check_inconsist(df, '医院编码', '医院级别', 'left')}
    d_error = {**d_error, **check_inconsist(df, '医院编码', '开户进展', 'left')}
    d_error = {**d_error, **check_inconsist(df, '医院全称', '省/自治区/直辖市', 'left')}
    d_error = {**d_error, **check_inconsist(df, '医院全称', '是否双call', 'left')}
    d_error = {**d_error, **check_inconsist(df, '医院全称', '医院级别', 'left')}
    d_error = {**d_error, **check_inconsist(df, '医院全称', '开户进展', 'left')}
    return d_error


def check_inconsist(df, col1, col2, side='left'):
    d_error = {}
    pivot = df.groupby([col1, col2]).size().reset_index().rename(columns={0: '记录数'})
    if side == 'left':
        if len(pivot[col1]) - len(pivot[col1].drop_duplicates()) > 0:
            d_error['相同' + col1 + '有不同' + col2] = \
                pivot[pivot.duplicated(col1, keep=False)].to_html(index=False, classes='ui red small table')
    elif side == 'right':
        if len(pivot[col2]) - len(pivot[col2].drop_duplicates()) > 0:
            d_error['相同' + col2 + '有不同' + col1] = \
                pivot[pivot.duplicated(col2, keep=False)].to_html(index=False, classes='ui red small table')
    elif side == 'both':
        if len(pivot[col1]) - len(pivot[col1].drop_duplicates()) > 0:
            d_error['相同' + col1 + '有不同' + col2] = \
                pivot[pivot.duplicated(col1, keep=False)].to_html(index=False, classes='ui red small table')
        if len(pivot[col2]) - len(pivot[col2].drop_duplicates()) > 0:
            d_error['相同' + col2 + '有不同' + col1] = \
                pivot[pivot.duplicated(col2, keep=False)].to_html(index=False, classes='ui red small table')
    return d_error


def dsm_auth(user, dsm_list):
    if user.is_staff:
        return True, None
    else:
        staffs = Staff.objects.get(name=user).get_descendants(include_self=True)
        staff_list = [i.name for i in staffs]
        return set(dsm_list).issubset(staff_list), set(dsm_list) - set(staff_list)


def get_df_clients(user):
    if user.is_staff:
        clients = Client.objects.all()
        df_clients = pd.DataFrame(list(clients.values()))
    else:
        staffs = Staff.objects.get(name=user).get_descendants(include_self=True)
        staff_list = [i.name for i in staffs]

        clients = Client.objects.filter(rd__in=staff_list) | Client.objects.filter(
            rm__in=staff_list) | Client.objects.filter(dsm__in=staff_list)
        df_clients = pd.DataFrame(list(clients.values()))
    if df_clients.empty is False:
        df_new = df_clients.reindex(columns=['rd', 'rm', 'dsm', 'rsp', 'xlt_id', 'hospital', 'province', 'dual_call',
                                             'hp_level', 'hp_access', 'name', 'dept', 'title', 'consulting_times',
                                             'patients_half_day', 'target_prop', 'note'])

        df_new['dual_call'] = df_new['dual_call'].map(D_MAP)
        df_new['hp_access'] = df_new['hp_access'].map(D_MAP)
        df_new['note'].fillna('', inplace=True)
        df_new['target_prop'] = df_new['target_prop']/100
        df_new['monthly_target_patients'] = round(df_new['consulting_times']*df_new['patients_half_day']*df_new['target_prop'], 0)
        df_new['potential_level'] = df_new['monthly_target_patients'].apply(
            lambda x: 'L' if x < 80 else ('M' if x < 200 else 'H'))

        df_new.columns = COL_REINDEX

        return df_new
    else:
        return pd.DataFrame()


def df_to_table(df, ignore_columns=None):
    if ignore_columns is not None and df.empty is False:
        df.drop(columns=ignore_columns, inplace=True)
    if df.empty is False:
        table = df.to_html(formatters=build_formatters_by_col(df), classes='ui celled small table',
                               table_id='table', escape=False, index=False)
        return table
    else:
        return "无记录"


def import_record(df):
    df = df.replace({np.nan: None})
    df['是否双call'] = df['是否双call'].map(D_MAP)
    df['开户进展'] = df['开户进展'].map(D_MAP)

    Client.objects.filter(dsm__in=df['地区经理'].unique()).delete()

    for index, row in df.iterrows():
        client = Client.objects.update_or_create(rd=row[COL[0]],
                                                 rm=row[COL[1]],
                                                 dsm=row[COL[2]],
                                                 rsp=row[COL[3]],
                                                 xlt_id=row[COL[4]],
                                                 hospital=row[COL[5]],
                                                 province=row[COL[6]],
                                                 dual_call=row[COL[7]],
                                                 hp_level=row[COL[8]],
                                                 hp_access=row[COL[9]],
                                                 name=row[COL[10]],
                                                 dept=row[COL[11]],
                                                 title=row[COL[12]],
                                                 consulting_times=row[COL[13]],
                                                 patients_half_day=row[COL[14]],
                                                 target_prop=row[COL[15]],
                                                 note=row[COL[16]]
                                                 )


def row_refined(matched):
    string = matched.group()[2:]
    row_n = int(string) + 2
    string = str(row_n)
    return string
