from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'clientfile'
urlpatterns = [
    path(r'', RedirectView.as_view(url='/clientfile/clients')),
    path(r'clients', views.clients, name='clients'),
    path(r'import_excel/', views.import_excel, name='import_excel'),  # 导入记录
    path(r'export_clients/', views.export_clients, name='export_clients'),  # 导出记录
    path(r'analysis', views.analysis, name='analysis'),  # 分析现有档案
    path(r'history', views.history, name='history'),  # 分析现有档案
    path(r'ajax_chart/<str:chart>/', views.ChartView.as_view(), name='ajax_chart'),  # Ajax出图
    path(r'ajax_table/<str:index>/', views.ajax_table, name='ajax_table'),  # Ajax出表
]