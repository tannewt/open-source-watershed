from django import template
register = template.Library()
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
