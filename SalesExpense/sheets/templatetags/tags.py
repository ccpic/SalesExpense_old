from django import template
from ..models import Record
from django.contrib.auth.models import User

register = template.Library()

# @register.simple_tag
# def active(request, pattern):
#     import re
#     if re.search(pattern, request.path):
#         return 'active'
#     return ''

@register.filter
def get_record(Record, pk):
    obj = Record.get(pk=int(pk))
    return obj


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def multiply(value, arg):
    try:
        if arg:
            return value * arg
    except: pass
    return ''


@register.filter(name='times')
def times(number):
    try:
        return range(1, number+1)
    except:
        return []


@register.filter(name='select_id')
def select_id(str):
    try:
        if str[-2:] == "[]":
            return str[:-2]
        else:
            return  str
    except:
        return str


@register.filter(name='modifier')
def modifier(str):
    try:
        action = str.split('|')[1]
        user = str.split('|')[2]
        if action == 'False':
            action = '添加'
        elif action == 'True':
            action = '删除'
        # elif action == '~':
        #     action = '修改'
        # user_id = int(float(str.split('|')[2]))
        # user = User.objects.get(id=user_id).username
        return "%s%s了" % (user, action)
    except:
        return str

@register.filter(name='modified_date')
def modified_date(str):
    try:
        date = str.split('|')[0]
        return date
    except:
        return str


@register.filter(name='modified_action')
def modified_action(str):
    try:
        action = str.split('|')[1]
        return action
    except:
        return str


@register.filter(name='none_to_blank')
def none_to_blank(str):
    try:
        if str is None:
            return ''
        else:
            return str
    except:
        return str


@register.filter(name='percentage')
def percentage(value, decimal):
    try:
        format_str = '{0:.'+ str(decimal) + '%}'
        return format_str.format(value)
    except:
        return value


@register.filter(name='value_to_color')
def value_to_color(value):
    try:
        if value > 0.8:
            return 'green'
        elif value > 0.6:
            return 'olive'
        elif value > 0.4:
            return 'yellow'
        elif value > 0.2:
            return 'orange'
        else:
            return 'red'
    except:
        return ''
