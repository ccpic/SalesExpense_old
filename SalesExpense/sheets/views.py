from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Hospital, Record, Staff
import datetime, time
import pandas as pd
import numpy as np
from django.http import JsonResponse
from django.core import serializers

try:
    from io import BytesIO as IO  # for modern python
except ImportError:
    from io import StringIO as IO  # for legacy python

pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 5000)


@login_required()
def records(request):
    hospitals = Hospital.objects.all()
    records = Record.objects.all()
    context = {'table': get_df_records(request.user),
               'hospital_list': hospitals,
               'record_list': records,
               'month_range': range(1, 13),
               'year_range': range(2019, 2021)
               }
    return render(request, 'sheets/records.html', context)


@login_required()
def hospitals(request):
    hospitals = Hospital.objects.all()
    dsm_list = Staff.objects._mptt_filter(level=3)
    context = {
        'table': get_df_hospitals(request.user),
        'hospital_list': hospitals,
        'dsm_list': dsm_list,
    }
    return render(request, 'sheets/hospitals.html', context)


def detail(request, rsp_name):
    hospital = Hospital.objects.filter(rsp=rsp_name)
    record = Record.objects.filter(hospital__in=hospital)
    return render(request, 'sheets/detail.html', {'record': record})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


'''添加医院'''


@login_required()
def ajax_add_hospital(request):
    if request.method == 'POST':
        xltid = request.POST.get('xltid')
        name = request.POST.get('name')
        rsp = request.POST.get('rsp')
        dsm_id = request.POST.get('dsm')
        Hospital.objects.create(xltid=xltid, name=name, rsp=rsp, dsm=Staff.objects.get(id=dsm_id))

    return HttpResponse(get_df_hospitals(request.user))


'''删除医院'''


@login_required()
def ajax_delete_hospital(request):
    if request.method == "POST":
        id = request.POST.get('id')
        qs_to_delete = Hospital.objects.filter(id=id)  # 执行删除操作
        qs_to_delete.delete()
        return HttpResponse(get_df_hospitals(request.user))


'''根据id获取记录'''


@login_required()
def ajax_get_record(request):
    if request.method == "POST":
        id = request.POST.get('id')
        record = serializers.serialize('json', Record.objects.filter(id=id))
        return JsonResponse(record, safe=False)


'''添加记录'''


@login_required()
def ajax_add_record(request):
    if request.method == 'POST':
        hospital_id = request.POST.get('hospital_id')
        record_date = datetime.datetime(year=int(request.POST.get('year')),
                                        month=int(request.POST.get('month')),
                                        day=1)
        note_text = request.POST.get('note_text')
        hospital_sales = request.POST.get('hospital_sales')
        project1_volume = request.POST.get('project1_volume')
        project2_volume = request.POST.get('project2_volume')
        cp_expense = request.POST.get('cp_expense')
        round_table_times = request.POST.get('round_table_times')
        round_table_expense = request.POST.get('round_table_expense')
        print(hospital_id, record_date, note_text, hospital_sales, project1_volume, project2_volume, cp_expense,
              round_table_times, round_table_expense)
        if Record.objects.filter(hospital=Hospital.objects.get(pk=hospital_id), record_date=record_date).exists():
            return HttpResponse('existed')
        else:
            Record.objects.create(hospital=Hospital.objects.get(pk=hospital_id), record_date=record_date,
                                  note_text=note_text,
                                  hospital_sales=hospital_sales, project1_volume=project1_volume,
                                  project2_volume=project2_volume,
                                  cp_expense=cp_expense, round_table_times=round_table_times,
                                  round_table_expense=round_table_expense
                                  )

            return HttpResponse(get_df_records(request.user))


'''删除记录'''


@login_required()
def ajax_delete_record(request):
    if request.method == "POST":
        id = request.POST.get('id')
        qs_to_delete = Record.objects.filter(id=id)
        qs_to_delete.delete()
        return HttpResponse(get_df_records(request.user))


'''删除记录'''


@login_required()
def ajax_modify_record(request):
    if request.method == "POST":
        record_id = request.POST.get('record_id')
        note_text = request.POST.get('note_text')
        hospital_sales = request.POST.get('hospital_sales')
        project1_volume = request.POST.get('project1_volume')
        project2_volume = request.POST.get('project2_volume')
        cp_expense = request.POST.get('cp_expense')
        round_table_times = request.POST.get('round_table_times')
        round_table_expense = request.POST.get('round_table_expense')
        print(record_id, note_text, hospital_sales, project1_volume, project2_volume, cp_expense,
              round_table_times, round_table_expense)
        record = Record.objects.get(id=record_id)
        record.note_text = note_text
        record.hospital_sales = hospital_sales
        record.project1_volume = project1_volume
        record.project2_volume = project2_volume
        record.cp_expense = cp_expense
        record.round_table_times = round_table_times
        record.round_table_expense = round_table_expense
        record.save()

        return HttpResponse(get_df_records(request.user))


'''导出记录'''


@login_required()
def export_record(request):
    df = get_df_records(request.user, False)
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


def get_df_records(user, table=True):
    if user.is_staff:
        staffs = Staff.objects.all()
        df_staffs = pd.DataFrame(list(staffs.values()))

        hospitals = Hospital.objects.all()
        df_hospitals = pd.DataFrame(list(hospitals.values()))

        records = Record.objects.order_by('-pub_date')
        df_records = pd.DataFrame(list(records.values()))
    else:
        staffs = Staff.objects.get(name=user).get_descendants(include_self=True)
        df_staffs = pd.DataFrame(list(staffs.values()))

        hospitals = Hospital.objects.filter(dsm__in=Staff.objects.get(name=user).get_descendants(include_self=True))
        df_hospitals = pd.DataFrame(list(hospitals.values()))

        print(Staff.objects.get(name=user).get_descendants(include_self=True))
        records = Record.objects.filter(
            hospital__dsm__in=Staff.objects.get(name=user).get_descendants(include_self=True)).order_by('-pub_date')
        df_records = pd.DataFrame(list(records.values()))
    if df_staffs.empty is False and df_hospitals.empty is False and df_records.empty is False:
        df = pd.merge(df_hospitals, df_staffs, how='left', left_on='dsm_id', right_on='id', sort=True)
        df = pd.merge(df_records, df, how='left', left_on='hospital_id', right_on='id_x', sort=True)
        df['year'] = df['record_date'].dt.tz_convert('Asia/Shanghai').dt.year
        df['month'] = df['record_date'].dt.tz_convert('Asia/Shanghai').dt.month
        project1_price = 25
        df['project1_expense'] = df['project1_volume'] * project1_price
        project2_price = 25
        df['project2_expense'] = df['project2_volume'] * project2_price
        df['cp_volume'] = df['hospital_sales'] - df['project1_volume'] - df['project2_volume']
        cp_price = 8
        df['cp_budget'] = df['cp_volume'] * cp_price
        df['total_expense1'] = df['project1_expense'] + df['project2_expense'] + df['cp_expense']
        df['ce_ratio1'] = df['total_expense1'] / df['hospital_sales']
        df['total_expense2'] = df['total_expense1'] + df['round_table_expense']
        df['ce_ratio2'] = df['total_expense2'] / df['hospital_sales']

        df_new = df.reindex(columns=['id', 'year', 'month', 'name_y', 'rsp', 'name_x', 'hospital_sales',
                                     'project1_volume', 'project1_expense', 'project2_volume', 'project2_expense',
                                     'cp_volume', 'cp_budget', 'cp_expense', 'total_expense1', 'ce_ratio1',
                                     'round_table_times', 'round_table_expense', 'total_expense2', 'ce_ratio2'])
        if table is True:
            df_new.columns = ['操作', '年', '月', '地区经理', '代表', '医院名称', '进货盒数', 'PMS盒数', 'PMS金额',
                              'TRUE盒数', 'TRUE金额', 'CP盒数', 'CP预算', 'CP报销', '合计金额1', '费效比1',
                              '科室会数量', '科室会报销', '合计金额2', '费效比2']
            # <a href="javascript:void(0);" onclick=""><i class="edit icon"></i></a>
            df_new['操作'] = df_new['操作'].apply(lambda x:
                                              '<div data-tooltip="修改" data-position="top left">'
                                              '<a href="javascript:void(0);" onclick="modify_record({0});">'
                                              '<i class="edit icon"></i></a></div>'
                                              '<div data-tooltip="删除" data-position="top left">'
                                              '<a href="javascript:void(0);" onclick="delete_record({0});">'
                                              '<i class="x icon"></i></a></div>'
                                              .format(x))
            table = df_new.to_html(formatters=build_formatters_by_col(df_new),
                                   classes='ui celled table', table_id='table', escape=False, index=False)
            return table
        else:
            df_new.columns = ['Record_id', '年', '月', '地区经理', '代表', '医院名称', '进货盒数', 'PMS盒数', 'PMS金额',
                              'TRUE盒数', 'TRUE金额', 'CP盒数', 'CP预算', 'CP报销', '合计金额1', '费效比1',
                              '科室会数量', '科室会报销', '合计金额2', '费效比2']
            return df_new
    else:
        return "无记录"


def get_df_hospitals(user):
    if user.is_staff:
        staffs = Staff.objects.all()
        df_staffs = pd.DataFrame(list(staffs.values()))

        hospitals = Hospital.objects.all()
        df_hospitals = pd.DataFrame(list(hospitals.values()))
    else:
        staffs = Staff.objects.get(name=user).get_descendants(include_self=True)
        df_staffs = pd.DataFrame(list(staffs.values()))

        hospitals = Hospital.objects.filter(dsm__in=Staff.objects.get(name=user).get_descendants(include_self=True))
        df_hospitals = pd.DataFrame(list(hospitals.values()))
    if df_staffs.empty is False and df_hospitals.empty is False:
        df = pd.merge(df_hospitals, df_staffs, how='left', left_on='dsm_id', right_on='id', sort=True)
        df_new = df.reindex(columns=['id_x', 'xltid', 'name_x', 'rsp', 'name_y'])
        df_new.columns = ['id', '信立泰医院编码', '医院名称', '负责代表', '所属地区经理']
        # df['操作'] = df['操作'].apply(lambda x: '<a href="javascript:void(0);" onclick="delete_hospital({0});">删除</a>'.format(x))
        table = df_new.to_html(formatters=build_formatters_by_col(df),
                               classes='ui celled table', table_id='table', escape=False, index=False)
        return table
    else:
        return "无记录"


def build_formatters(df, format):
    d = {}
    for (column, dtype) in df.dtypes.iteritems():
        if dtype in [np.dtype('int64'), np.dtype('float64')]:
            d[column] = format
    return d


def build_formatters_by_col(df):
    format_currency = lambda x: '¥{:,.0f}'.format(x)
    format_phone = lambda x: '{:.0f}'.format(x)
    format_abs = lambda x: '{:,.0f}'.format(x)
    format_share = lambda x: '{:.0%}'.format(x)
    format_gr = lambda x: '{:.1%}'.format(x)
    format_ratio = lambda x: '{:,.1f}'.format(x)
    d = {}
    for (column, dtype) in df.dtypes.iteritems():
        if column == '年' or column == '月':
            pass
        elif '份额' in column or '贡献' in column or '比例' in column or '%' in column:
            d[column] = format_share
        elif '价格' in column or '单价' in column or '金额' in column:
            d[column] = format_currency
        elif '同比增长' in column or '增长率' in column or 'CAGR' in column or '同比变化' in column:
            d[column] = format_gr
        elif '费效比' in column:
            d[column] = format_ratio
        elif '电话' in column:
            d[column] = format_phone
        else:
            if dtype in [np.dtype('int64'), np.dtype('float64')]:
                d[column] = format_abs
    return d
