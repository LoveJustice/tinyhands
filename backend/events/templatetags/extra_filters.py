from django import template
register = template.Library()

from django import template
register = template.Library()


@register.filter(name='css_class')
def css_class(field, css):
    return field.as_widget(attrs={"class":css})


@register.filter(name='is_boolean')
def is_boolean(field):
    return (field.field.__class__.__name__ == "BooleanField")


@register.filter(name='is_multiplechoice')
def is_multiplechoice(field):
    return field.field.__class__.__name__ == "ModelMultipleChoiceField"