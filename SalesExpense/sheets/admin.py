from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from .models import Hospital, Record, Staff


class StaffAdmin(DjangoMpttAdmin):
    pass


admin.site.register(Staff, StaffAdmin)

