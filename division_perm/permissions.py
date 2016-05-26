# coding: utf-8
from rest_framework.permissions import BasePermission


class DivisionAccess(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'employee')

    def has_object_permission(self, request, view, obj):
        is_modify = request.method.upper == 'GET'
        if is_modify:
            return obj.can_employee_modify(request.user.employee)
        else:
            return obj.can_employee_read(request.user.employee)
