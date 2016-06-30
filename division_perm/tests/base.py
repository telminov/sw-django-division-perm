# coding: utf-8
from .. import consts
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase
from division_perm import models


class BaseTest(TestCase):
    view_path = None

    def setUp(self): # todo: fixture, как-то хитро загружается
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        self.empl = models.Employee.objects.create(user=self.user, last_name='test', first_name='test', middle_name='test')
        func_read = models.Func.objects.create(code=consts.SYS_READ_FUNC, name='test_read', level=0)
        models.Func.objects.create(code=consts.SYS_EDIT_FUNC, name='test_edit', level=0)
        self.division = models.Division.objects.create(name='TechSupport')
        self.division.employees.add(self.empl)
        role_read = models.Role.objects.create(name='Manager', code=func_read.code, level=9, division=self.division)
        self.empl.roles.add(role_read)
        self.empl.full_access.add(self.division)
        self.division.full_access.add(self.division)
        self.client.login(username=self.user.username, password='123')

    def get_url(self):
        url = reverse(self.view_path)