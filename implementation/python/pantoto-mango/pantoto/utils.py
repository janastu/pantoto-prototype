from django.http import Http404
from django.template.defaultfilters import slugify

def to_classname(value):
    return "".join([ w.capitalize() for w in value.split('-') ])

def headerify(value):
    """
        Converts the String to a column header
    """
    return " ".join([ w.capitalize() for w in value.strip().split('_') ])

def underscorify(txt):
    return slugify(txt).strip().replace('-','_')

def to_bool(value):
    if value == 'True' or value == 'true' or value == '1' or value == 1:
        return True
    else:
        return False

