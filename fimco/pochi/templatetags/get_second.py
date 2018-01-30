from datetime import datetime
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='get_second')
@stringfilter
def get_second_value(value):
    return value.split(' ')[1]
