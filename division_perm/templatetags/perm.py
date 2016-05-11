# coding: utf-8
from django import template
from .. import models
register = template.Library()


@register.filter
def can_modify(obj, user):
    full_access_divisions = set(obj.get_full_access())
    employee_division = set(user.employee.divisions.all())
    have_access = bool(employee_division & full_access_divisions)
    return have_access


@register.simple_tag(takes_context=True)
def can_func(context, func_code, obj=None):
    user = context['user']
    func = models.Func.objects.get(code=func_code)

    if obj is not None and func.is_modify:
        can_modify_obj = can_modify(obj, user)
        if not can_modify_obj:
            return False

    # Если объект не задан, значи вопрос ставится:
    # "может ли пользователь в принципе хоть с каким-нибудь объектом выполнить эту функцию?".
    # Например, создать новый объект.
    if obj is None:
        divisions = user.employee.divisions.all()

    # В противном случае речь идет о правах на конкретный объект
    else:
        if func.is_modify:
            divisions = obj.get_full_access()
        else:
            divisions = obj.get_read_access()

    # определим максимальный уровень пользователя в рамках подразделений
    user_level = 0
    for role in user.employee.roles.all():
        if role.division in divisions and role.level > user_level:
            user_level = role.level

    user_can_func = func.level <= user_level
    return user_can_func


@register.inclusion_tag('division_perm/can_func_tag.html', takes_context=True)
def block_super_if_can_func(context, func_code, obj=None):
    user_can_func = can_func(context, func_code, obj=obj)
    return {
        'user_can_func': user_can_func,
        'content': context['block'].super,
    }

