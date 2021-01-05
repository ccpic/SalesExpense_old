# -*- coding: utf-8 -*-
from django.shortcuts import render
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
from django.db import IntegrityError
from pandas_schema import Column, Schema
from pandas_schema.validation import (
    LeadingWhitespaceValidation,
    TrailingWhitespaceValidation,
    CanConvertValidation,
    MatchesPatternValidation,
    InRangeValidation,
    InListValidation,
    CustomElementValidation,
    IsDistinctValidation,
)
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core import serializers
import scipy.stats as stats
from django.db.models import Max

try:
    from io import BytesIO as IO  # for modern python
except ImportError:
    from io import StringIO as IO  # for legacy python

pd.set_option("display.max_columns", 5000)
pd.set_option("display.width", 5000)


D_SEARCH_FIELD = {
    "省/自治区/直辖市": "province",
    "南北中国": "bu",
    "区域": "rd",
    "大区": "rm",
    "地区经理": "dsm",
    "负责代表": "rsp",
    "医院全称": "hospital",
    "医院级别": "hp_level",
    "客户姓名": "name",
    "所在科室": "dept",
    "职称": "title",
    #"备注": "note",
}

D_SELECT = {
    "省/自治区/直辖市": "province-select[]",
    "南北中国": "bu-select[]",
    "区域": "rd-select[]",
    "大区": "rm-select[]",
    "地区经理": "dsm-select[]",
    "负责代表": "rsp-select[]",
    "医院编码": "xltid-select[]",
    "医院全称": "hosp-select[]",
    "是否双call": "dc-select[]",
    "医院级别": "hplevel-select[]",
    "是否开户": "hpaccess-select[]",
    "所在科室": "dept-select[]",
    "职称": "title-select[]",
}

D_FIELD = {
    "省/自治区/直辖市": "province",
    "南北中国": "bu",
    "区域": "rd",
    "大区": "rm",
    "地区经理": "dsm",
    "负责代表": "rsp",
    "医院编码": "xlt_id",
    "医院全称": "hospital",
    "是否双call": "dual_call",
    "医院级别": "hp_level",
    "是否开户": "hp_access",
    "所在科室": "dept",
    "职称": "title",
}

D_MAP = {
    "已开户": True,
    "未开户": False,
    "是": True,
    "否": False,
    True: "是",
    False: "否",
}

D_TRANSLATE = {
    "nan": "",
    "row": "行",
    "column": "列",
    "contains trailing whitespace": "末尾含有空白字符",
    "contains leading whitespace": "起始含有空白字符",
    "is not in the list of legal options": "不在下列合法选项中",
    'does not match the pattern "^[H]{1}(\d){9}$"': '格式不符合"字母H开头跟随9位数字"',
    "contains values that are not unique": "含有和该列其他单元格重复的数据",
    "cannot be converted to type": "必须为整数",
    "was not in the range": "超出了该字段允许的范围",
}

COL = [
    "南北中国",
    "区域",
    "大区",
    "地区经理",
    "负责代表",
    "医院编码",
    "医院全称",
    "省/自治区/直辖市",
    "是否双call",
    "医院级别",
    "开户进展",
    "客户姓名",
    "所在科室",
    "职称",
    "月出诊次数（半天计）",
    "每半天\n门诊量",
    "相关病人\n比例(%)\n建议比例：40%-80%",
    "备注",
]

COL_REINDEX = [
    "南北中国",
    "区域",
    "大区",
    "地区经理",
    "负责代表",
    "医院编码",
    "医院全称",
    "省/自治区/直辖市",
    "是否双call",
    "医院级别",
    "是否开户",
    "客户姓名",
    "所在科室",
    "职称",
    "月出诊次数（半天计）",
    "每半天门诊量",
    "相关病人比例(%)",
    "备注",
    "月累计相关病人数",
    "潜力级别",
]


@login_required()
def clients(request):
    if request.method == "GET":
        record_n = get_clients(request.user).count
        context = {"record_n": record_n}
        return render(request, "clientfile/clients.html", context)
    else:
        # 查询常数设置
        ORDER_DICT = {
            0: "bu",
            1: "rd",
            2: "rm",
            3: "dsm",
            4: "rsp",
            5: "hospital",
            6: "hp_level",
            7: "name",
            8: "dept",
            9: "title",
            10: "consulting_times",
            11: "patients_half_day",
            12: "target_prop",
            13: "note",
            14: "monthly_target_patients",
            15: "potential_level",
        }

        dataTable = {}
        aodata = json.loads(request.POST.get("aodata"))

        for item in aodata:
            if item["name"] == "sEcho":
                sEcho = int(item["value"])  # 客户端发送的标识
            if item["name"] == "iDisplayStart":
                start = int(item["value"])  # 起始索引
            if item["name"] == "iDisplayLength":
                length = int(item["value"])  # 每页显示的行数
            if item["name"] == "iSortCol_0":
                sort_column = int(item["value"])  # 按第几列排序
            if item["name"] == "sSortDir_0":
                sort_order = item["value"].lower()  # 正序还是反序
            if item["name"] == "sSearch":
                search_key = item["value"]  # 搜索关键字

        # 根据前端返回筛选参数筛选
        context = get_context_from_form(request)

        # 根据用户权限，前端参数，搜索关键字返回client objects
        clients = get_clients(request.user, context, search_key)

        # 排序
        result_length = clients.count()
        if sort_column < 43:
            if sort_order == "asc":
                clients = sorted(clients, key=lambda a: getattr(a, ORDER_DICT[sort_column]))
            elif sort_order == "desc":
                clients = sorted(clients, key=lambda a: getattr(a, ORDER_DICT[sort_column]), reverse=True)
        elif sort_column == 14:
            if sort_order == "asc":
                clients = sorted(clients, key=lambda a: a.monthly_patients())
            elif sort_order == "desc":
                clients = sorted(clients, key=lambda a: a.monthly_patients(), reverse=True)
        elif sort_column == 15:
            if sort_order == "asc":
                clients = sorted(clients, key=lambda a: a.potential_level())
            elif sort_order == "desc":
                clients = sorted(clients, key=lambda a: a.potential_level(), reverse=True)

        # 对list进行分页
        paginator = Paginator(clients, length)
        # 把数据分成10个一页。
        try:
            clients = paginator.page(start / 10 + 1)
        # 请求页数错误
        except PageNotAnInteger:
            clients = paginator.page(1)
        except EmptyPage:
            clients = paginator.page(paginator.num_pages)
        data = []
        for item in clients:
            if item.potential_level() == 1:
                potential_level = "L"
            elif item.potential_level() == 2:
                potential_level = "M"
            elif item.potential_level() == 3:
                potential_level = "H"
            row = {
                "bu": item.bu,
                "rd": item.rd,
                "rm": item.rm,
                "dsm": item.dsm,
                "rsp": item.rsp,
                # "xlt_id": item.xlt_id,
                "hospital": item.hospital,
                # "province": item.province,
                # "dual_call": item.dual_call,
                "hp_level": item.hp_level,
                # "hp_access": item.hp_access,
                "name": '<a href="/clientfile/clients/%s">%s</a>' % (item.pk, item.name),
                "dept": item.dept,
                "title": item.title,
                "consulting_times": item.consulting_times,
                "patients_half_day": item.patients_half_day,
                "target_prop": "{:.0%}".format(item.target_prop / 100),
                "note": item.note,
                "monthly_target_patients": item.monthly_patients(),
                "potential_level": potential_level,
            }
            data.append(row)
        dataTable["iTotalRecords"] = result_length  # 数据总条数
        dataTable["sEcho"] = sEcho + 1
        dataTable["iTotalDisplayRecords"] = result_length  # 显示的条数
        dataTable["aaData"] = data

        return HttpResponse(json.dumps(dataTable, ensure_ascii=False))


@login_required()
def client_detail(request, id):
    client = Client.objects.get(pk=id)
    client_monthly_patients = client.monthly_patients()
    groups = Group.objects.filter(clients__pk=id)

    # 全国潜力分位
    pct_rank = get_pct_rank(client_monthly_patients, Client.objects.all())

    # 同医院潜力分位
    clients_same_hosp = Client.objects.filter(hospital=client.hospital)
    pct_rank_same_hosp = get_pct_rank(client_monthly_patients, clients_same_hosp)

    # 同医院同科室潜力分位
    clients_same_hosp_dept = Client.objects.filter(hospital=client.hospital, dept=client.dept)
    pct_rank_same_hosp_dept = get_pct_rank(client_monthly_patients, clients_same_hosp_dept)
    clients_same_hosp_dept = clients_same_hosp_dept.exclude(pk=id)

    # 同医院同科室同职称潜力分位
    clients_same_hosp_dept_title = Client.objects.filter(hospital=client.hospital, dept=client.dept, title=client.title)
    pct_rank_same_hosp_dept_title = get_pct_rank(client_monthly_patients, clients_same_hosp_dept_title)

    # 同省份潜力分位
    clients_same_province = Client.objects.filter(province=client.province)
    pct_rank_same_province = get_pct_rank(client_monthly_patients, clients_same_province)

    # 同bu潜力分位
    clients_same_bu = Client.objects.filter(bu=client.bu)
    pct_rank_same_bu = get_pct_rank(client_monthly_patients, clients_same_bu)

    # 同rd潜力分位
    clients_same_rd = Client.objects.filter(rd=client.rd)
    pct_rank_same_rd = get_pct_rank(client_monthly_patients, clients_same_rd)

    # 同rm潜力分位
    clients_same_rm = Client.objects.filter(rm=client.rm)
    pct_rank_same_rm = get_pct_rank(client_monthly_patients, clients_same_rm)

    # 同dsm潜力分位
    clients_same_dsm = Client.objects.filter(dsm=client.dsm)
    pct_rank_same_dsm = get_pct_rank(client_monthly_patients, clients_same_dsm)

    # 同rsp潜力分位
    clients_same_rsp = Client.objects.filter(rsp=client.rsp)
    pct_rank_same_rsp = get_pct_rank(client_monthly_patients, clients_same_rsp)

    # 同DSM相似潜力医生
    client_monthly_patients_lb = client_monthly_patients * 0.95
    client_monthly_patients_ub = client_monthly_patients * 1.05
    related_ids = [
        client.id
        for client in clients_same_dsm
        if client_monthly_patients_lb < client.monthly_patients() < client_monthly_patients_ub
    ]
    clients_related = Client.objects.filter(id__in=related_ids)
    clients_related = clients_related.exclude(pk=id)

    context = {
        "client": client,
        "groups": groups,
        "clients_related": clients_related,
        "clients_same_hosp_dept": clients_same_hosp_dept,
        "pct_rank": pct_rank,
        "pct_rank_same_hosp": pct_rank_same_hosp,
        "pct_rank_same_hosp_dept": pct_rank_same_hosp_dept,
        "pct_rank_same_hosp_dept_title": pct_rank_same_hosp_dept_title,
        "pct_rank_same_province": pct_rank_same_province,
        "pct_rank_same_bu": pct_rank_same_bu,
        "pct_rank_same_rd": pct_rank_same_rd,
        "pct_rank_same_rm": pct_rank_same_rm,
        "pct_rank_same_dsm": pct_rank_same_dsm,
        "pct_rank_same_rsp": pct_rank_same_rsp,
    }

    return render(request, "clientfile/client_detail.html", context)


@login_required()
def export_clients(request):
    df = get_df_clients(request.user)
    excel_file = IO()

    xlwriter = pd.ExcelWriter(excel_file, engine="xlsxwriter")

    df.to_excel(xlwriter, "data", index=False)

    xlwriter.save()
    xlwriter.close()

    excel_file.seek(0)

    # 设置浏览器mime类型
    response = HttpResponse(
        excel_file.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 设置文件名
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    response["Content-Disposition"] = "attachment; filename=" + now + ".xlsx"
    return response


@login_required()
def import_excel(request):
    SHEET_NAME = "客户档案"
    context = {"code": 0, "msg": ""}
    if request.method == "POST":
        excel_file = request.FILES.get("attachmentName")
        if excel_file is None:  # 检查没有选择本地文件就直接点击上传的错误
            context["msg"] = "没有选择本地文件"
            return JsonResponse(context)
        else:
            try:
                df = pd.read_excel(excel_file, sheet_name=SHEET_NAME)  # 检查目标工作表不存在错误
            except xlrd.biffh.XLRDError as e:
                if "No sheet" in e.args[0]:
                    context["msg"] = '上传Excel没有名为"' + SHEET_NAME + '"的工作表'
                else:
                    context["msg"] = "读取Excel文件错误"
                return JsonResponse(context)
            else:
                if set(COL).issubset(df.columns) is False:  # 检查读取工作表表头时字段名不匹配错误
                    column_diff = set(COL) - set(list(df.columns.values))  # 缺少的字段列表
                    context["msg"] = "缺少以下必须字段，请检查" + str(column_diff)
                    return JsonResponse(context)
                else:
                    if dsm_auth(request.user, df["地区经理"].unique())[0] is False:  # 权限检查，只能上传自己/下属dsm的数据
                        context["msg"] = "权限错误，只能上传自己/下属dsm的数据，你没有权限上传下列dsm的数据" + str(
                            dsm_auth(request.user, df[COL[3]].unique())[1]
                        )
                        return JsonResponse(context)
                    else:
                        d_error = validate(df)
                        if d_error:
                            for key, value in d_error.items():
                                context["msg"] += key + d_error[key]
                            return JsonResponse(context)
                        else:
                            try:
                                import_record(df)
                            except IntegrityError as e:
                                context["msg"] = "文件中有记录(代表-医院-科室-客户姓名）与其他账号上传数据重复，请联系管理员解决"
                                return JsonResponse(context)
                            else:
                                context["code"] = 1
                                context["msg"] = "上传成功，可以尝试" + '<a href="analysis">分析现有数据</a>'
                                return JsonResponse(context)


def validate(df):
    d_error = {}
    list_bu = [x[0] for x in BU_CHOICES]
    list_rd = [x[0] for x in RD_CHOICES]
    list_dept = [x[0] for x in DEPT_CHOICES]
    list_hplevel = [x[0] for x in HPLEVEL_CHOICES]
    list_province = [x[0] for x in PROVINCE_CHOICES]
    list_title = [x[0] for x in TITLE_CHOICES]

    NullValidation = CustomElementValidation(lambda d: d is not np.nan, "该字段不能为空")
    schema = Schema(
        [
            Column("南北中国", [InListValidation(list_bu)]),
            Column("区域", [InListValidation(list_rd)]),
            Column("大区", [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
            Column("地区经理", [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
            Column("负责代表", [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
            Column(
                "医院编码",
                [
                    LeadingWhitespaceValidation(),
                    TrailingWhitespaceValidation(),
                    NullValidation,
                    MatchesPatternValidation(r"^[H]{1}(\d){9}$"),
                ],
            ),
            Column("医院全称", [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), NullValidation]),
            Column("省/自治区/直辖市", [InListValidation(list_province)]),
            Column("是否双call", [InListValidation(["是", "否"])]),
            Column("医院级别", [InListValidation(list_hplevel)]),
            Column("开户进展", [InListValidation(["已开户", "未开户"])]),
            Column("客户姓名", [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), IsDistinctValidation()]),
            Column("所在科室", [InListValidation(list_dept)]),
            Column("职称", [InListValidation(list_title)]),
            Column("月出诊次数（半天计）", [CanConvertValidation(int), InRangeValidation(0, 63)]),
            Column("每半天\n门诊量", [CanConvertValidation(int), InRangeValidation(0,)]),
            Column("相关病人\n比例(%)\n建议比例：40%-80%", [CanConvertValidation(int), InRangeValidation(0, 101)]),
            Column("备注"),
        ]
    )
    errors = schema.validate(df.loc[:, COL])
    for error in errors:
        str_warning = str(error)
        for term in D_TRANSLATE:
            str_warning = str_warning.replace(term, D_TRANSLATE[term])
            findword = r": [0-9]\d*"
            str_warning = re.sub(findword, row_refined, str_warning)
        d_error[str_warning] = "<br>"

    d_error = {**d_error, **check_inconsist(df, "医院编码", "医院全称", "both")}
    d_error = {**d_error, **check_inconsist(df, "区域", "大区", "right")}
    d_error = {**d_error, **check_inconsist(df, "大区", "地区经理", "right")}
    d_error = {**d_error, **check_inconsist(df, "地区经理", "负责代表", "right")}
    d_error = {**d_error, **check_inconsist(df, "医院编码", "省/自治区/直辖市", "left")}
    d_error = {**d_error, **check_inconsist(df, "医院编码", "是否双call", "left")}
    d_error = {**d_error, **check_inconsist(df, "医院编码", "医院级别", "left")}
    d_error = {**d_error, **check_inconsist(df, "医院编码", "开户进展", "left")}
    d_error = {**d_error, **check_inconsist(df, "医院全称", "省/自治区/直辖市", "left")}
    d_error = {**d_error, **check_inconsist(df, "医院全称", "是否双call", "left")}
    d_error = {**d_error, **check_inconsist(df, "医院全称", "医院级别", "left")}
    d_error = {**d_error, **check_inconsist(df, "医院全称", "开户进展", "left")}

    d_error = {**d_error, **check_hplevel_with_dept(df)} # 检查医院级别和所在科室是否出现矛盾
    return d_error


def check_inconsist(df, col1, col2, side="left"):
    d_error = {}
    pivot = df.groupby([col1, col2]).size().reset_index().rename(columns={0: "记录数"})
    if side == "left":
        if len(pivot[col1]) - len(pivot[col1].drop_duplicates()) > 0:
            d_error["相同" + col1 + "有不同" + col2] = pivot[pivot.duplicated(col1, keep=False)].to_html(
                index=False, classes="ui red small table"
            )
    elif side == "right":
        if len(pivot[col2]) - len(pivot[col2].drop_duplicates()) > 0:
            d_error["相同" + col2 + "有不同" + col1] = pivot[pivot.duplicated(col2, keep=False)].to_html(
                index=False, classes="ui red small table"
            )
    elif side == "both":
        if len(pivot[col1]) - len(pivot[col1].drop_duplicates()) > 0:
            d_error["相同" + col1 + "有不同" + col2] = pivot[pivot.duplicated(col1, keep=False)].to_html(
                index=False, classes="ui red small table"
            )
        if len(pivot[col2]) - len(pivot[col2].drop_duplicates()) > 0:
            d_error["相同" + col2 + "有不同" + col1] = pivot[pivot.duplicated(col2, keep=False)].to_html(
                index=False, classes="ui red small table"
            )
    return d_error


def check_hplevel_with_dept(df):
    d_error = {}
    pivot = df.groupby(['医院级别', '所在科室']).size().reset_index().rename(columns={0: "记录数"})
    mask = (pivot['医院级别'].str.count('社区') + pivot['所在科室'].str.count('社区')) == 1
    if len(pivot.loc[mask, :]) > 0:
        d_error["医院级别和所在科室出现矛盾"] = pivot.loc[mask, :].to_html(
            index=False, classes="ui red small table")

    return d_error


def dsm_auth(user, dsm_list):
    if user.is_staff:
        return True, None
    else:
        staffs = Staff.objects.get(name=user).get_descendants(include_self=True)
        staff_list = [i.name for i in staffs]
        return set(dsm_list).issubset(staff_list), set(dsm_list) - set(staff_list)


def get_clients(
    user, context=None, search_key=None, is_deleted=False, group_id=None, pub_date_gte=None, name_and_hosp=None
):
    or_condiction = Q()

    if context is not None:
        for key, value in D_FIELD.items():
            if len(context[key]) > 0:
                if key in ["是否双call", "是否开户"]:
                    context[key] = [D_MAP[x] if x in D_MAP else x for x in context[key]]
                or_condiction.add(Q(**{"{}__in".format(value): context[key]}), Q.AND)

    # 根据前端Datatables搜索框筛选
    if search_key is not None and search_key != "":
        for key, value in D_SEARCH_FIELD.items():
            or_condiction.add(Q(**{"{}__contains".format(value): search_key}), Q.OR)

    if name_and_hosp is not None and name_and_hosp != "":
        keywords = name_and_hosp.split()
        print(len(keywords))
        if len(keywords) == 1:
            or_condiction.add(Q(name__contains=keywords[0]) | Q(hospital__contains=keywords[0]), Q.AND)
        elif len(keywords) == 2:
            or_condiction.add(Q(name__contains=keywords[0]), Q.AND)
            or_condiction.add(Q(hospital__contains=keywords[1]), Q.AND)

    if group_id is not None:
        or_condiction.add(Q(group__id=group_id), Q.AND)

    if pub_date_gte is not None:
        or_condiction.add(Q(pub_date__gte=pub_date_gte), Q.AND)

    # 根据参数决定是否显示假删除数据
    if is_deleted is False:
        clientset = Client.objects.all()
    elif is_deleted is True:
        clientset = Client.objects.all_with_deleted()

    # 根据用户权限筛选
    if user.is_staff:

        clients = clientset.filter(or_condiction)
    else:
        staffs = Staff.objects.get(name=user).get_descendants(include_self=True)
        staff_list = [i.name for i in staffs]

        clients = (
            clientset.filter(rd__in=staff_list)
            | clientset.filter(rm__in=staff_list)
            | clientset.filter(dsm__in=staff_list)
        )
        clients = clients.filter(or_condiction)
    return clients


def client_search(response, kw):
    clients_obj = get_clients(user=response.user, name_and_hosp=kw)
    print("search")
    try:
        clients = serializers.serialize("json", clients_obj, ensure_ascii=False)
        res = {
            "data": clients,
            "code": 200,
        }
        print(clients)
    except Exception as e:
        res = {
            "errMsg": e,
            "code": 0,
        }
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json charset=utf-8")


def get_df_clients(user, context=None, search_key=None, is_deleted=False, group_id=None, pub_date_gte=None):

    clients = get_clients(
        user=user,
        context=context,
        search_key=search_key,
        is_deleted=is_deleted,
        group_id=group_id,
        pub_date_gte=pub_date_gte,
    )
    df_clients = pd.DataFrame(list(clients.values()))
    if df_clients.empty is False:
        df_new = df_clients.reindex(
            columns=[
                "bu",
                "rd",
                "rm",
                "dsm",
                "rsp",
                "xlt_id",
                "hospital",
                "province",
                "dual_call",
                "hp_level",
                "hp_access",
                "name",
                "dept",
                "title",
                "consulting_times",
                "patients_half_day",
                "target_prop",
                "note",
            ]
        )

        df_new["dual_call"] = df_new["dual_call"].map(D_MAP)
        df_new["hp_access"] = df_new["hp_access"].map(D_MAP)
        df_new["note"].fillna("", inplace=True)
        df_new["target_prop"] = df_new["target_prop"] / 100
        df_new["monthly_target_patients"] = round(
            df_new["consulting_times"] * df_new["patients_half_day"] * df_new["target_prop"], 0
        )
        df_new["potential_level"] = df_new["monthly_target_patients"].apply(
            lambda x: "L" if x < 80 else ("M" if x < 200 else "H")
        )
        # df_new['hp_decile'] = django_method_to_df(clients)

        df_new.columns = COL_REINDEX
        return df_new
    else:
        return pd.DataFrame()


# def django_method_to_df(objs_django):
#     l =[]
#     for obj in objs_django:
#         l.append(obj.hp_decile())
#     return l


def df_to_table(df, ignore_columns=None):
    if ignore_columns is not None and df.empty is False:
        df.drop(columns=ignore_columns, inplace=True)
        table = df.to_html(
            formatters=build_formatters_by_col(df),
            classes="ui celled small table",
            table_id="table",
            escape=False,
            index=False,
        )
        return table
    else:
        return "无记录"


def import_record(df):
    df = df.replace({np.nan: None})
    df["是否双call"] = df["是否双call"].map(D_MAP)
    df["开户进展"] = df["开户进展"].map(D_MAP)

    Client.objects.filter(dsm__in=df["地区经理"].unique()).delete()  # 删除当前DSM名下的记录

    max_pub_id_entry = Client.objects.max_pub_id()  # 当前最大（晚更新）的pub_id
    if max_pub_id_entry is None:
        pub_id = 0
    else:
        pub_id = max_pub_id_entry + 1

    for index, row in df.iterrows():
        client = Client.objects.update_or_create(
            bu=row[COL[0]],
            rd=row[COL[1]],
            rm=row[COL[2]],
            dsm=row[COL[3]],
            rsp=row[COL[4]],
            xlt_id=row[COL[5]],
            hospital=row[COL[6]],
            province=row[COL[7]],
            dual_call=row[COL[8]],
            hp_level=row[COL[9]],
            hp_access=row[COL[10]],
            name=row[COL[11]],
            dept=row[COL[12]],
            title=row[COL[13]],
            consulting_times=row[COL[14]],
            patients_half_day=row[COL[15]],
            target_prop=row[COL[16]],
            note=row[COL[17]],
            pub_id=pub_id,
        )


def row_refined(matched):
    string = matched.group()[2:]
    row_n = int(string) + 2
    string = str(row_n)
    return string


def get_context_from_form(request, download_url=False):
    context = {}
    D_SELECT["table_id"] = "table_id"
    for key, value in D_SELECT.items():
        if request.method == "POST":
            if value[-2:] == "[]":
                selected = request.POST.getlist(value)
            else:
                selected = request.POST.get(value)
        elif request.method == "GET":
            if value[-2:] == "[]":
                if download_url is False:
                    selected = request.GET.getlist(value)
                else:
                    selected = request.GET.getlist(value[:-2])
            else:
                if download_url is False:
                    selected = request.GET.get(value)
                else:
                    selected = request.GET.get(value[:-2])
        context[key] = selected
    return context


def get_pct_rank(value, queryset_clients):
    """计算潜力在queryset档案中的百分位排名"""
    list_potential = []
    for client in queryset_clients:
        list_potential.append(client.monthly_patients())
    pct_rank = stats.percentileofscore(list_potential, value, kind="strict") / 100
    return pct_rank
