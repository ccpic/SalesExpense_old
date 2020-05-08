from django.contrib import admin
from .models import Client, Group, Hp_IQVIA


class ClientAdmin(admin.ModelAdmin):
    search_fields = ['bu', 'rd', 'rm', 'dsm', 'rsp', 'hospital',  'dept', 'name']

# Register your models here.

admin.site.register(Client, ClientAdmin)
admin.site.register([Group, Hp_IQVIA])

