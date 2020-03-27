from django.db import models
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models import Q, UniqueConstraint


class SoftDeleteQuerySet(QuerySet):
    #https://stackoverflow.com/questions/28896237/override-djangos-model-delete-method-for-bulk-deletion
    def __init__(self,*args,**kwargs):
        return super(self.__class__,self).__init__(*args,**kwargs)

    def delete(self,*args,**kwargs):
        for obj in self: obj.delete()


class SoftDeletableManager(models.Manager):
    """ Use this manager to get objects that have a is_deleted field """
    def get_queryset(self,*args,**kwargs):
        return SoftDeleteQuerySet(model=self.model, using=self._db, hints=self._hints).filter(is_deleted=False)

    def all_with_deleted(self,*args,**kwargs):
        return SoftDeleteQuerySet(model=self.model, using=self._db, hints=self._hints).filter()

    def deleted_set(self,*args,**kwargs):
        return SoftDeleteQuerySet(model=self.model, using=self._db, hints=self._hints).filter(is_deleted=True)

    def get(self, *args, **kwargs):
        """ if a specific record was requested, return it even if it's deleted """
        return self.all_with_deleted().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        """ if pk was specified as a kwarg, return even if it's deleted """
        if 'pk' in kwargs:
            return self.all_with_deleted().filter(*args, **kwargs)
        return self.get_queryset().filter(*args, **kwargs)


class SoftDeletableModel(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name='软删除')

    class Meta:
        abstract = True

    objects = SoftDeletableManager()

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        这里需要真删除的话soft=False即可
        """
        if soft:
            self.is_deleted = True
            self.save(using=using)
        else:
            return super(SoftDeletableModel, self).delete(using=using, *args, **kwargs)


HPLEVEL_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('旗舰社区', '旗舰社区'),
    ('普通社区', '普通社区'),
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
TITLE_CHOICES = [
    ('院长', '院长'),
    ('副院长', '副院长'),
    ('主任医师', '主任医师'),
    ('副主任医师', '副主任医师'),
    ('主治医师', '主治医师'),
    ('住院医师', '住院医师'),
    ('其他', '其他'),
]

class Client(SoftDeletableModel):
    rd = models.CharField(max_length=10, verbose_name='所属区域')
    rm = models.CharField(max_length=10, verbose_name='所属大区')
    dsm = models.CharField(max_length=10, verbose_name='所属经理')
    rsp = models.CharField(max_length=10, verbose_name='负责代表')
    xlt_id = models.CharField(max_length=10, verbose_name='医院编码')
    hospital = models.CharField(max_length=100, verbose_name='医院全称')
    province = models.CharField(max_length=10, choices=PROVINCE_CHOICES, verbose_name='省/自治区/直辖市')
    dual_call = models.BooleanField(verbose_name='是否双call')
    hp_level = models.CharField(max_length=4, choices=HPLEVEL_CHOICES, verbose_name='医院级别')
    hp_access = models.BooleanField(verbose_name='开户进展')
    dept = models.CharField(max_length=4, choices=DEPT_CHOICES, verbose_name='所在科室')
    name = models.CharField(max_length=10, verbose_name='客户姓名')
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, verbose_name='职称')
    # phone = models.IntegerField(verbose_name='客户联系电话', null=True, blank=True)
    consulting_times = models.IntegerField(verbose_name='月出诊次数（半天计）')
    patients_half_day = models.IntegerField(verbose_name='每半天门诊量')
    target_prop = models.IntegerField(verbose_name='相关病人比例(%)')
    # monthly_prescription = models.IntegerField(verbose_name='当前月处方量')
    note = models.CharField(max_length=100, verbose_name='备注', null=True, blank=True)
    pub_date = models.DateTimeField(verbose_name='上传日期',auto_now=True)

    class Meta:
        verbose_name = '客户档案'
        verbose_name_plural = '客户档案'
        ordering = ['rd', 'rm', 'dsm', 'rsp', 'hospital', 'dept', 'name']
        # unique_together = ('rsp', 'hospital', 'dept', 'name')
        constraints = [
            UniqueConstraint(fields=['rsp', 'hospital', 'dept', 'name'], condition=Q(is_deleted=False),
                             name='unique_if_not_deleted')
        ]

    def __str__(self):
        return "%s %s %s %s %s %s %s" % (self.rd, self.rm, self.dsm, self.rsp, self.hospital, self.dept, self.name)

    def monthly_patients(self):
        return round(self.consulting_times * self.patients_half_day * self.target_prop / 100, 0)

    def potential_level(self):
        if self.monthly_patients() < 80:
            return 1
        elif self.monthly_patients() < 200:
            return 2
        else:
            return 3

    # def favor_level(self):
    #     if self.monthly_prescription <= 20:
    #         return 1
    #     elif self.monthly_prescription <= 100:
    #         return 2
    #     elif self.monthly_prescription <= 300:
    #         return 3
    #     else:
    #         return 4


class Group(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建用户')
    name = models.CharField(max_length=50, verbose_name='分组名称')
    clients = models.ManyToManyField(Client)
    note = models.CharField(max_length=100, verbose_name='备注', null=True, blank=True)
    pub_date = models.DateTimeField(verbose_name='创建日期', auto_now=True)

    def __str__(self):
        return self.name