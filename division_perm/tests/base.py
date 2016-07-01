# coding: utf-8
from .. import consts
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase
from division_perm import models


class BaseTest(TestCase):
    view_path = None
    fixtures = ['perm_func']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        other_user = User.objects.create_user(username='other_user', email='other_user@soft-way.biz', password='123')
        empl = models.Employee.objects.create(user=self.user, last_name='other_test', first_name='other_test', middle_name='other_test')
        other_empl = models.Employee.objects.create(user=other_user, last_name='test', first_name='test', middle_name='test')
        func_edit = models.Func.objects.get(code=consts.SYS_EDIT_FUNC)
        division = models.Division.objects.create(name='TechSupport')
        division.employees.add(empl)
        role_edit = models.Role.objects.create(name='Manager', code=func_edit.code, level=9, division=division)
        empl.roles.add(role_edit)
        empl.full_access.add(division)
        other_empl.full_access.add(division)
        division.full_access.add(division)
        self.client.login(username=self.user.username, password='123')

        self.generate_data()

    def get_url(self):
        url = reverse(self.view_path)
        return url