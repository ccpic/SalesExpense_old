from django.contrib import admin
from .models import Client


class ClientAdmin(admin.ModelAdmin):
    search_fields = ['rd', 'rm', 'dsm', 'rsp', 'hospital',  'dept', 'name']

# Register your models here.
admin.site.register(Client, ClientAdmin)

