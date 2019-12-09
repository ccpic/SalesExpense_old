#!/usr/bin/env python
import pandas as pd
import os, sys

import time, datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SalesExpense.settings")
import django
django.setup()

from django.contrib.auth.models import User
from sheets.models import Staff


def importRecord():
    df = pd.read_excel(io="../费用管理.xlsx")

    from sheets.models import Record,Hospital

    l = []
    for r in df.values:
        hospital_sales = int(r[6])
        project1_volume = int(r[7])
        project2_volume = int(r[9])
        cp_expense = int(r[13])
        round_table_times = int(r[16])
        round_table_expense = int(r[17])
        if Hospital.objects.filter(xltid=r[4], name=r[5], rsp=r[3], dsm=r[2]).exists():
            hospital = Hospital.objects.get(xltid=r[4], name=r[5], rsp=r[3], dsm=r[2])
        else:
            hospital = Hospital.objects.create(xltid=r[4], name=r[5], rsp=r[3], dsm=r[2])
        record = Record(hospital=hospital,
                        hospital_sales=hospital_sales,
                        project1_volume=project1_volume,
                        project2_volume=project2_volume,
                        cp_expense=cp_expense,
                        round_table_times=round_table_times,
                        round_table_expense=round_table_expense,
                        record_date=datetime.datetime(year=2019, month=int(r[1]), day=1),
                        pub_date= datetime.datetime.now(),
                        note_text= "",
        )
        l.append((record))

    Record.objects.bulk_create(l)


if __name__ == "__main__":
    for user in User.objects.all():
        password = 'Luna1117'
        print(user.username, password)
        user.set_password(password)
        user.save()
    # start = time.clock()
    # importRecord()
    # print('Done!', time.clock()-start)