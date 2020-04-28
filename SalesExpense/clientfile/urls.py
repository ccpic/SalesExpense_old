from django.urls import path
from django.views.generic import RedirectView
from . import views_clients, views_analysis, views_history, views_groups

app_name = 'clientfile'
urlpatterns = [
    path(r'', RedirectView.as_view(url='/clientfile/clients')),
    path(r'clients', views_clients.clients, name='clients'),
    path(r'clients/search/<str:kw>', views_clients.client_search, name='client_search'),
    path(r'clients/<int:id>/', views_clients.client_detail, name='client_detail'), #单个客户细节
    path(r'import_excel/', views_clients.import_excel, name='import_excel'),  # 导入记录
    path(r'export_clients/', views_clients.export_clients, name='export_clients'),  # 导出档案记录
    path(r'groups/export', views_groups.export_groups, name='export_groups'),  # 导出客户事件记录
    path(r'analysis', views_analysis.analysis, name='analysis'),  # 分析现有档案
    path(r'ajax_chart/<str:chart>/', views_analysis.ChartView.as_view(), name='ajax_chart'),  # Ajax出图
    path(r'ajax_table/<str:index>/', views_analysis.ajax_table, name='ajax_table'),  # Ajax出表
    path(r'history', views_history.history, name='history'),  # 档案记录
    path(r'groups', views_groups.groups, name='groups'),  # 客户分组事件
    path(r'groups/<int:id>/', views_groups.group_detail, name='group_detail'),  # 单个客户分组细节
    path(r'groups/add', views_groups.add_group, name='add_group'),  # 添加新客户分组事件
    path(r'groups/delete', views_groups.delete_group, name='delete_group'),  # 删除客户分组事件
]
