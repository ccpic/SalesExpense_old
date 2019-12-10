from django.db import models
# from month.models import MonthField
from mptt.models import MPTTModel


class Staff(MPTTModel):
    name = models.CharField('姓名', max_length=10, unique=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, verbose_name='上级人员', null=True, blank=True, related_name='children')

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '团队架构'
        db_table = 'staff'

    def __str__(self):
        return self.name


class Hospital(models.Model):
    xltid = models.CharField(max_length=10, verbose_name='信立泰医院id')
    name = models.CharField(max_length=30, verbose_name='医院名称')
    rsp = models.CharField(max_length=10, verbose_name='负责代表')
    dsm = models.ForeignKey(Staff, on_delete=models.PROTECT, verbose_name='所属大区')

    class Meta:
        verbose_name = '医院-代表'
        verbose_name_plural = '医院-代表'
        ordering = ['name', 'rsp', 'dsm']

    def __str__(self):
        return str(self.xltid) + str(self.name) + '(' + str(self.rsp) + ')'


class Record(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, verbose_name='医院')
    hospital_sales = models.IntegerField(default=0, verbose_name='医院进货盒数')
    project1_volume = models.IntegerField(default=0, verbose_name='PMS盒数')
    project2_volume = models.IntegerField(default=0, verbose_name='True盒数')
    cp_expense = models.IntegerField(default=0, verbose_name='CP实际报销金额')
    round_table_times = models.IntegerField(default=0, verbose_name='科室会次数')
    round_table_expense = models.IntegerField(default=0, verbose_name='科室会和点评会报销金额')
    record_date = models.DateTimeField(verbose_name='记录日期')
    pub_date = models.DateTimeField(verbose_name='上传日期',auto_now=True)
    note_text = models.CharField(max_length=200, blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = '费用记录'
        verbose_name_plural = '费用记录'
        ordering = ['hospital__name', 'hospital__rsp', 'record_date']

    def __str__(self):
        return self.hospital.name + ' '+ self.hospital.rsp +  ' '+ self.record_date.strftime("%Y-%m")

