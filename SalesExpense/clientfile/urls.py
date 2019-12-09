from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'clientfile'
urlpatterns = [
    path(r'', RedirectView.as_view(url='/clientfile/clients')),
    path(r'clients', views.clients, name='clients'),
    path(r'import_excel/', views.import_excel, name='import_excel'), #导入记录
    path(r'export_clients/', views.export_clients, name='export_clients'), #导出记录
    path(r'analysis', views.analysis, name='analysis'), #分析现有档案
    path(r'ajax_chart/<str:chart>/', views.ChartView.as_view(), name='ajax_chart'), #Ajax出图
    path(r'ajax_table/<str:index>/', views.ajax_table, name='ajax_table') #Ajax出表
    # path(r'hospitals', views.hospitals, name='hospitals'),
    # path('records/<str:rsp_name>/detail/', views.detail, name='detail'),
    # # ex: /polls/5/results/
    # path('<int:record_id>/results/', views.results, name='results'),
    # # ex: /polls/5/vote/
    # path(r'export_record/', views.export_record, name='export_record'), #导出记录
    # path(r'get_add_record/', views.ajax_get_record, name='ajax_get_record'), #根据id获取记录
    # path(r'ajax_add_record/', views.ajax_add_record, name='ajax_add_record'), #添加记录
    # path(r'ajax_delete_record/', views.ajax_delete_record, name='ajax_delete_record'), #删除记录
    # path(r'ajax_modify_record/', views.ajax_modify_record, name='ajax_modify_record'), #删除记录
    # path(r'ajax_add_hospital/', views.ajax_add_hospital, name='ajax_add_hospital'),  # 添加医院
    # path(r'ajax_delete_hospital/', views.ajax_delete_hospital, name='ajax_delete_hospital'),  # 删除医院
]