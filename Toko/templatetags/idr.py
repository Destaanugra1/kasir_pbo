from django import template

register = template.Library()

@register.filter
def idr(value):
    try:
        value = int(value)
        return "Rp{:,.0f}".format(value).replace(",", ".")
    except:
        return value