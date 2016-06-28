# coding: utf-8
from django.conf import settings
from django.conf.urls import url

import division_perm.views.func
import division_perm.views.division
import division_perm.views.role
import division_perm.views.employee
import division_perm.views.rest


urlpatterns = [
    url(r'^func/$', division_perm.views.func.List.as_view(), name='perm_func_list'),
    url(r'^func/(?P<pk>\d+)/$', division_perm.views.func.Detail.as_view(), name='perm_func_detail'),

    url(r'^employee/$', division_perm.views.employee.List.as_view(), name='perm_employee_list'),
    url(r'^employee/create/$', division_perm.views.employee.Create.as_view(), name='perm_employee_create'),
    url(r'^employee/(?P<pk>\d+)/$', division_perm.views.employee.Detail.as_view(), name='perm_employee_detail'),
    url(r'^employee/(?P<pk>\d+)/edit/$', division_perm.views.employee.Update.as_view(), name='perm_employee_update'),
    url(r'^employee/(?P<pk>\d+)/roles_edit/$', division_perm.views.employee.Roles.as_view(), name='perm_employee_roles'),
    url(r'^employee/(?P<pk>\d+)/delete/$', division_perm.views.employee.Delete.as_view(), name='perm_employee_delete'),
    url(r'^employee/(?P<pk>\d+)/password_change/$', division_perm.views.employee.PasswordChange.as_view(),
        name='perm_employee_password_change'),

    url(r'^division/$', division_perm.views.division.List.as_view(), name='perm_division_list'),
    url(r'^division/create/$', division_perm.views.division.Create.as_view(), name='perm_division_create'),
    url(r'^division/(?P<pk>\d+)/$', division_perm.views.division.Detail.as_view(), name='perm_division_detail'),
    url(r'^division/(?P<pk>\d+)/edit/$', division_perm.views.division.Update.as_view(), name='perm_division_update'),
    url(r'^division/(?P<pk>\d+)/delete/$', division_perm.views.division.Delete.as_view(), name='perm_division_delete'),

    url(r'^division/(?P<division_pk>\d+)/role/create/$', division_perm.views.role.Create.as_view(), name='perm_role_create'),
    url(r'^division/(?P<division_pk>\d+)/role/(?P<pk>\d+)/$', division_perm.views.role.Detail.as_view(), name='perm_role_detail'),
    url(r'^division/(?P<division_pk>\d+)/role/(?P<pk>\d+)/edit/$', division_perm.views.role.Update.as_view(), name='perm_role_update'),
    url(r'^division/(?P<division_pk>\d+)/role/(?P<pk>\d+)/delete/$', division_perm.views.role.Delete.as_view(), name='perm_role_delete'),

]


if settings.DEBUG:
    urlpatterns += [
        url(r'^generate_sig/$', division_perm.views.rest.generate_sig),
        url(r'^hello/$', division_perm.views.rest.hello),
    ]
