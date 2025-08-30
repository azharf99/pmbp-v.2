from django import template

from utils.constants import QURAN_SURAH_DICT
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_quran_name(dictionary, key):
    return QURAN_SURAH_DICT.get(str(key))

@register.filter
def to(value, end):
    return range(value, end + 1)