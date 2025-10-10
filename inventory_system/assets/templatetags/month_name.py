from django import template

register = template.Library()

MONTHS_RU = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

@register.filter
def month_name(value):
    """Преобразует номер месяца в русское название"""
    try:
        value = int(value)
        return MONTHS_RU.get(value, "")
    except (ValueError, TypeError):
        return ""
