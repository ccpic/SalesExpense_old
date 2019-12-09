from django import template
from ..models import Record

register = template.Library()

@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''

@register.filter
def get_record(Record, pk):
    print(pk)
    obj = Record.get(pk=int(pk))
    return obj
