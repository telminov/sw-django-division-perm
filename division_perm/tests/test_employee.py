# coding: utf-8

from .. import consts
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase
from division_perm import models

class BaseEmployee(TestCase):
    view_path = None

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        self.empl = models.Employee.objects.create(user=self.user, last_name='test', first_name='test', middle_name='test')
        func_read = models.Func.objects.create(code=consts.SYS_READ_FUNC, name='test_read', level=0)
        func_edit = models.Func.objects.create(code=consts.SYS_EDIT_FUNC, name='test_edit', level=0)
        self.division = models.Division.objects.create(name='Тех. поддержка')
        self.division.employees.add(self.empl)

        role = models.Role.objects.create(name='манеджер', code=func_read.code, level=2, division=self.division)
        self.empl.roles.add(role)
        self.client.login(username=self.user.username, password='123')

    def get_url(self):
        url = reverse(self.view_path)
        return url


class EmployeeList(BaseEmployee):
    view_path = 'perm_employee_list'

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
        self.empl.read_access.add(self.division)
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)

    def test_empty_object(self):
        self.empl.read_access.clear()
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 0)


class EmployeeDetail(BaseEmployee):
    view_path = 'perm_employee_detail'

    def get_url(self):
        url = reverse(self.view_path, args=[self.empl.id])
        return url

    def test_detail_403(self):
        self.empl.read_access.clear()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_detail_200(self):
        self.empl.read_access.add(self.division)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.empl, response.context['object'])


class EmployeeCreate(BaseEmployee):
    view_path = 'perm_employee_create'

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        p = {
            'username': u'ivanov',
            'password1': 't1234567',
            'password2': 't1234567',
            'last_name': u'Иванов',
            'first_name': u'Иван',
            'middle_name': u'Иванович',
            # 'divisions': [self.division.id,],
            'full_access': str(self.division.id),
            # 'read_access': [self.division.id,],
            'is_active': True,
            'can_external': False,
        }

        response = self.client.post(self.get_url(), p)
        self.assertEqual(response.status_code, 200)
        print (response.context['form'].errors)
        created_empl = models.Employee.objects.filter(username=p['username'])[0]


        self.assertEqual(created_empl.last_name, p['last_name'])
        self.assertEqual(created_empl.first_name, p['first_name'])
        self.assertEqual(created_empl.middle_name, p['middle_name'])

