from django import template
register = template.Library()
from django.utils.safestring import mark_safe
import datetime

@register.filter(name='prettydelta')
def prettydelta(value):
  if value==None:
    return "-"
  elif value == datetime.timedelta(0):
    return "-"
  elif value < datetime.timedelta(7):
    return str(value.days)+"d"
  elif value < datetime.timedelta(1):
    return str(value.seconds/60/60)+"h"
  else:
    return str(value.days/7)+"w"

@register.filter(name='highlight')
def highlight(value, sub, autoescape=None):
  if sub not in value:
    return value
  i = value.index(sub)
  return mark_safe(value[:i] + "<strong>" + value[i:i+len(sub)] + "</strong>" + value[i+len(sub):])
highlight.needs_autoescape = True
