# coding: utf-8
from .. import consts
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase
from division_perm import models


class EmployeeList(TestCase):
    view_path = 'perm_employee_list'

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        empl = models.Employee.objects.create(user=self.user, last_name='test', first_name='test', middle_name='test')
        func_read = models.Func.objects.create(code=consts.SYS_READ_FUNC, name='test_read', level=0)
        func_edit = models.Func.objects.create(code=consts.SYS_EDIT_FUNC, name='test_edit', level=0)
        division = models.Division.objects.create(name='IT')
        division.employees.add(empl)
        role = models.Role.objects.create(name='манеджер', code=func_read.code, level=2, division=division)
        empl.roles.add(role)
        self.client.login(username=self.user.username, password='123')

    def get_url(self):
        url = reverse(self.view_path)
        return url

    def test_403(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_200(self):
        self.client.login(username=self.user.username, password='123')
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(
            response.redirect_chain[0],
            ('/perm/employee/?sort=last_name', 302)
        )

    def test_object(self):
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'], 1)

