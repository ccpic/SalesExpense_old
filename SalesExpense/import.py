#!/usr/bin/env python
import pandas as pd
import os, sys

import time, datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SalesExpense.settings")
import django
django.setup()

from django.contrib.auth.models import User
from clientfile.models import Hp_IQVIA


def importIQVIA():
    df = pd.read_excel(io="../Decile.xlsx", sheet_name='医院潜力数据', header=2)

    l = []
    for r in df.values:
        xlt_id = r[3]
        name = r[4]
        province = r[5]
        city = r[6]
        if r[11] == '目标医院':
            is_target = True
        else:
            is_target = False
        potential = int(r[13])
        decile = r[14]
        potential_rank = r[15]
        print(xlt_id, name, province, city, is_target, potential, decile, potential_rank)
        hospital = Hp_IQVIA(xlt_id=xlt_id,
                            name = name,
                            province = province,
                            city = city,
                            is_target = is_target,
                            potential = potential,
                            decile = decile,
                            potential_rank = potential_rank
                            )
        l.append(hospital)

    Hp_IQVIA.objects.bulk_create(l)


if __name__ == "__main__":
    importIQVIA()
    # for user in User.objects.all():
    #     password = 'Luna1117'
    #     print(user.username, password)
    #     user.set_password(password)
    #     user.save()
