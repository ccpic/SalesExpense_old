from django.db import models

HPLEVEL_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
]
PROVINCE_CHOICES = [
    ('北京', '北京'),
    ('天津', '天津'),
    ('河北', '河北'),
    ('山西', '山西'),
    ('内蒙古', '内蒙古'),
    ('辽宁', '辽宁'),
    ('吉林', '吉林'),
    ('黑龙江', '黑龙江'),
    ('上海', '上海'),
    ('江苏', '江苏'),
    ('浙江', '浙江'),
    ('安徽', '安徽'),
    ('福建', '福建'),
    ('江西', '江西'),
    ('山东', '山东'),
    ('河南', '河南'),
    ('湖北', '湖北'),
    ('湖南', '湖南'),
    ('广东', '广东'),
    ('广西', '广西'),
    ('海南', '海南'),
    ('重庆', '重庆'),
    ('四川', '四川'),
    ('贵州', '贵州'),
    ('云南', '云南'),
    ('西藏', '西藏'),
    ('陕西', '陕西'),
    ('甘肃', '甘肃'),
    ('青海', '青海'),
    ('宁夏', '宁夏'),
    ('新疆', '新疆')
]
DEPT_CHOICES = [
    ('心内科', '心内科'),
    ('肾内科', '肾内科'),
    ('神内科', '神内科'),
    ('内分泌科', '内分泌科'),
    ('老干科', '老干科'),
    ('其他科室', '其他科室')
]
class Client(models.Model):
    rd = models.CharField(max_length=10, verbose_name='所属区域')
    rm = models.CharField(max_length=10, verbose_name='所属大区')
    dsm = models.CharField(max_length=10, verbose_name='所属经理')
    rsp = models.CharField(max_length=10, verbose_name='负责代表')
    xlt_id = models.CharField(max_length=10, verbose_name='医院编码')
    hospital = models.CharField(max_length=100, verbose_name='医院全称')
    province = models.CharField(max_length=10, choices=PROVINCE_CHOICES, verbose_name='省/自治区/直辖市')
    dual_call = models.BooleanField(verbose_name='是否双call')
    hp_level = models.CharField(max_length=1, choices=HPLEVEL_CHOICES, verbose_name='医院级别')
    hp_access = models.BooleanField(verbose_name='开户进展')
    dept = models.CharField(max_length=4, choices=DEPT_CHOICES, verbose_name='所在科室')
    name = models.CharField(max_length=10, verbose_name='客户姓名')
    title = models.CharField(max_length=10, verbose_name='职称')
    phone = models.IntegerField(verbose_name='客户联系电话', null=True, blank=True)
    consulting_times = models.IntegerField(verbose_name='月出诊次数（半天计）')
    patients_half_day = models.IntegerField(verbose_name='每半天门诊量')
    target_prop = models.IntegerField(verbose_name='相关病人比例(%)')
    monthly_prescription = models.IntegerField(verbose_name='当前月处方量')
    note = models.CharField(max_length=100, verbose_name='备注', null=True, blank=True)

    class Meta:
        verbose_name = '客户档案'
        ordering = ['rd', 'rm', 'dsm', 'rsp', 'hospital', 'dept', 'name']
        unique_together = ('rsp', 'hospital', 'dept', 'name')

    def __str__(self):
        return "%s %s %s %s %s %s %s" % (self.rd, self.rm, self.dsm, self.rsp, self.hospital, self.dept, self.name)