from django import template
from ..models import Record

register = template.Library()

# @register.simple_tag
# def active(request, pattern):
#     import re
#     if re.search(pattern, request.path):
#         return 'active'
#     return ''

@register.filter
def get_record(Record, pk):
    print(pk)
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
    print(number)
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



