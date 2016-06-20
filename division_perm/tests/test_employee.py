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
        self.empl.full_access.add(self.division)
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
        p = self.get_params()
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


class EmployeeUpdate(BaseEmployee):
    view_path = 'perm_employee_update'

    def get_url(self):
        url = reverse(self.view_path, args=[self.empl.id])
        return url

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        p = self.get_params()
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


class EmployeeDelete(BaseEmployee):
    view_path = 'perm_employee_delete'

    def get_url(self):
        url = reverse(self.view_path, args=[self.empl.id])
        return url

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_delete(self): # может стоит еще одно пользователя создать
        response = self.client.post(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Employee.objects.filter(id=self.empl.id).count(), 0)


class EmployeePasswordChange(BaseEmployee):
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


class EmployeeRoles(BaseEmployee):
    view_path = 'perm_employee_roles'

    def get_url(self):
        url = reverse(self.view_path, args=[self.empl.id])
        return url

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)