# coding: utf-8
from .. import consts
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase
from division_perm import models

class BaseRoleTest(TestCase):
    view_path = None

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        self.empl = models.Employee.objects.create(user=self.user, last_name='test', first_name='test', middle_name='test')
        func_edit = models.Func.objects.create(code=consts.SYS_EDIT_FUNC, name='test_edit', level=5)
        self.func_read = models.Func.objects.create(code=consts.SYS_READ_FUNC, name='test_read', level=0)
        self.division = models.Division.objects.create(name='Тех. поддержка')
        self.division.employees.add(self.empl)
        self.role_read = models.Role.objects.create(name='управляющий', code=self.func_read.code, level=9, division=self.division)
        self.empl.roles.add(self.role_read)
        self.division.full_access.add(self.division)
        self.client.login(username=self.user.username, password='123')

    def get_url(self):
        url = reverse(self.view_path)
        return url

    def get_param(self):
        p = {
            'division': self.division.id,
            'code': u'new_code',
            'name': u'new_role',
            'description': u'test_description',
            'level': 7,
            'employees': [self.empl.id],
        }
        return p

class RoleCreateTest(BaseRoleTest):
    view_path = 'perm_role_create'

    def get_url(self):
        url = reverse(self.view_path, args=[self.division.id])
        return url

    def test_403(self):
        self.division.full_access.clear()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        p = self.get_param()
        response = self.client.post(self.get_url(), p, follow=True)
        self.assertEqual(len(response.redirect_chain), 1)
        created_role = models.Role.objects.filter(name=p['name'])[0]
        self.assertEqual(response.redirect_chain[0], ('../..', 302))
        self.assertEqual(p['division'], created_role.division.id)
        self.assertEqual(p['code'], created_role.code)
        self.assertEqual(p['description'], created_role.description)
        self.assertEqual(p['level'], created_role.level)
        self.assertListEqual(p['employees'], list(created_role.employees.all().values_list('id', flat=True)))


class RoleDetailTest(BaseRoleTest):
    view_path = 'perm_role_detail'

    def get_url(self):
        url = reverse(self.view_path, args=[self.division.id, self.role_read.id])
        return url

    def test_detail_403(self):
        self.division.full_access.clear()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_detail_200(self):
        self.empl.read_access.add(self.division)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.role_read, response.context['object'])


class RoleUpdateTest(BaseRoleTest):
    view_path = 'perm_role_update'

    def get_url(self):
        url = reverse(self.view_path, args=[self.division.id, self.role_read.id])
        return url

    def test_detail_403(self):
        self.division.full_access.clear()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        p = self.get_param()
        response = self.client.post(self.get_url(), p, follow=True)
        # self.assertEqual(response.status_code, 200) todo: ошибка редиректа
        update_role = models.Role.objects.filter(name=p['name'])[0]
        self.assertEqual(response.redirect_chain[0], ('../../..', 302))
        self.assertEqual(p['division'], update_role.division.id)
        self.assertEqual(p['code'], update_role.code)
        self.assertEqual(p['description'], update_role.description)
        self.assertEqual(p['level'], update_role.level)
        self.assertListEqual(p['employees'], list(update_role.employees.all().values_list('id', flat=True)))


class RoleDeleteTest(BaseRoleTest):
    view_path = 'perm_role_delete'

    def get_url(self):
        url = reverse(self.view_path, args=[self.division.id, self.role_read.id])
        return url

    def test_403(self):
        self.division.full_access.clear()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post(self.get_url(), follow=True)
        # self.assertEqual(response.status_code, 403) todo: ошибка редиректа
        self.assertEqual(models.Role.objects.filter(id=self.role_read.id).count(), 0)