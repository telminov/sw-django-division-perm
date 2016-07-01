# coding: utf-8
from .. import consts
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from division_perm import models
from division_perm.tests.base import BaseTest
from division_perm.tests.helpers import *

class BaseEmployee(BaseTest):
    view_path = None

    def generate_data(self):
        self.empl = self.user.employee
        self.division = self.empl.divisions.all()[0]

    def get_emp_params(self):
        p = {
            'username': 'ivanov',
            'password1': 't1234567',
            'password2': 't1234567',
            'last_name': 'Ivanov',
            'first_name': 'Ivan',
            'middle_name': 'Ivanovich',
            'divisions': self.division.id,
            'full_access': self.division.id,
            'read_access': self.division.id,
            'is_active': True,
            'can_external': False,
        }
        return p


class EmployeeListTest(FuncAccessTestMixin, ListTestMixin, ListAccessTestMixin, BaseEmployee):
    view_path = 'perm_employee_list'
    success_url = reverse('perm_employee_list') + '?sort=last_name'
    model_access = models.Employee
    func_code = consts.SYS_READ_FUNC


class EmployeeDetailTest(BaseEmployee, DetailTestMixin, ReadAccessTestMixin):
    view_path = 'perm_employee_detail'
    model_access = models.Employee

    def get_instance(self):
        return self.empl

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url


class EmployeeCreateTest(BaseEmployee):
    view_path = 'perm_employee_create'

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        p = self.get_emp_params()
        response = self.client.post(self.get_url(), p, follow=True)
        self.assertEqual(len(response.redirect_chain), 1)
        created_empl = models.Employee.objects.filter(user__username=p['username'])[0]
        self.assertEqual(response.redirect_chain[0], ('/perm/employee/%s/' % created_empl.id, 302))
        self.assertEqual(p['last_name'], created_empl.last_name)
        self.assertEqual(p['first_name'], created_empl.first_name)
        self.assertEqual(p['middle_name'], created_empl.middle_name)
        self.assertIn(p['divisions'], created_empl.divisions.all().values_list('id', flat=True))
        self.assertIn(p['full_access'], created_empl.full_access.all().values_list('id', flat=True))
        self.assertIn(p['read_access'], created_empl.read_access.all().values_list('id', flat=True))
        self.assertEqual(p['is_active'], created_empl.user.is_active)
        self.assertEqual(p['can_external'], created_empl.can_external)


class EmployeeUpdateTest(BaseEmployee):
    view_path = 'perm_employee_update'

    def get_url(self):
        url = reverse(self.view_path, args=[self.empl.id])
        return url

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        p = self.get_emp_params()
        response = self.client.post(self.get_url(), p, follow=True)
        self.assertEqual(response.status_code, 200)
        update_empl = models.Employee.objects.get(id=self.empl.id)
        self.assertEqual(response.redirect_chain[0], ('/perm/employee/%s/' % update_empl.id, 302))
        self.assertEqual(p['last_name'], update_empl.last_name)
        self.assertEqual(p['first_name'], update_empl.first_name)
        self.assertEqual(p['middle_name'], update_empl.middle_name)
        self.assertIn(p['divisions'], update_empl.divisions.all().values_list('id', flat=True))
        self.assertIn(p['full_access'], update_empl.full_access.all().values_list('id', flat=True))
        self.assertIn(p['read_access'], update_empl.read_access.all().values_list('id', flat=True))
        self.assertEqual(p['is_active'], update_empl.user.is_active)
        self.assertEqual(p['can_external'], update_empl.can_external)


class EmployeeDeleteTest(BaseEmployee, DeleteTestMixin):
    view_path = 'perm_employee_delete'
    model = models.Employee

    def generate_data(self):
        self.other_empl = models.Employee.objects.exclude(id=self.user.employee.id)[0]

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url

    def get_instance(self):
        return self.other_empl


class EmployeePasswordChangeTest(BaseEmployee):
    view_path = 'perm_employee_password_change'

    def get_url(self):
        url = reverse(self.view_path, args=[self.empl.id])
        return url

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_change(self):
        new_password = u'new_password'
        old_password = self.empl.user.password
        p = {
            'password1': new_password,
            'password2': new_password,
        }
        response = self.client.post(self.get_url(), p, follow=True)
        self.assertEqual(response.redirect_chain[0], ('..', 302))
        update_empl = models.Employee.objects.get(id=self.empl.id)
        self.assertNotEqual(update_empl.user.password, old_password)


class EmployeeRolesTest(BaseEmployee):
    view_path = 'perm_employee_roles'

    def get_url(self):
        url = reverse(self.view_path, args=[self.empl.id])
        return url

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_edit_roles(self):
        role = models.Role.objects.get(code=consts.SYS_EDIT_FUNC)
        role.division = self.division
        role.save()

        p = {
            'user': self.empl.user,
            'roles': [role.id],
        }
        response = self.client.post(self.get_url(), p, follow=True)
        self.assertEqual(response.redirect_chain[0], ('/perm/employee/%s/' % self.empl.id, 302))
        self.assertIn(role, self.empl.roles.all())