# coding: utf-8

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase
from division_perm import models, views
from .. import consts
from division_perm.tests.helpers import ListTestMixin, ListAccessTestMixin, ReadAccessTestMixin, DetailTestMixin


class BaseDivision(TestCase):
    view_path = None

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        self.employee = models.Employee.objects.create(user=self.user, last_name='test', first_name='test', middle_name='test')
        func_edit = models.Func.objects.create(code=consts.SYS_EDIT_FUNC, name='test_edit', level=5)
        self.func_read = models.Func.objects.create(code=consts.SYS_READ_FUNC, name='test_read', level=0)
        self.division = models.Division.objects.create(name='Tech Support')
        self.division.employees.add(self.employee)
        self.division.read_access.add(self.division)
        role_read = models.Role.objects.create(name='manager', code=self.func_read.code, level=9, division=self.division)
        self.employee.roles.add(role_read)
        self.client.login(username=self.user.username, password='123')

    def get_url(self):
        url = reverse(self.view_path)
        return url

    def get_url_param(self, args):
        url = reverse(self.view_path, args=args)
        return url

    def get_param(self):
        p = {
            'name': 'Managers',
            'employees': [self.employee.id],
            'full_access': self.division.id,
            'read_access': self.division.id,
        }
        return p


class DivisionListTest(BaseDivision, ListTestMixin):
    view_path = 'perm_division_list'
    success_url = reverse('perm_division_list') + '?sort=name'
    model_access = models.Division


class DivisionDetailTest(BaseDivision, DetailTestMixin):
    view_path = 'perm_division_detail'

    def get_instance(self):
        return self.division

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url + '?role_sort=-level' # todo: возможно изменить логику тестового миксина


class DivisionCreateTest(BaseDivision):
    view_path = 'perm_division_create'

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        p = self.get_param()
        response = self.client.post(self.get_url(), p, follow=True)
        self.assertEqual(len(response.redirect_chain), 2)
        created_division = models.Division.objects.filter(name=p['name'])[0]
        self.assertEqual(response.redirect_chain[0], ('/perm/division/%s/' % created_division.id, 302))
        self.assertEqual(response.redirect_chain[1], ('/perm/division/%s/?role_sort=-level' % created_division.id, 302))
        self.assertEqual(p['name'], created_division.name)
        self.assertListEqual(p['employees'], list(created_division.employees.all().values_list('id', flat=True)))
        self.assertIn(p['full_access'], created_division.full_access.all().values_list('id', flat=True))
        self.assertIn(p['read_access'], created_division.read_access.all().values_list('id', flat=True))


class DivisionUpdateTest(BaseDivision):
    view_path = 'perm_division_update'

    def test_detail_403(self):
        self.division.full_access.clear()
        response = self.client.get(self.get_url_param([self.division.id]))
        self.assertEqual(response.status_code, 403)

    def test_200(self):
        self.division.full_access.add(self.division.id)
        response = self.client.get(self.get_url_param([self.division.id]))
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        self.division.full_access.add(self.division.id)
        p = self.get_param()
        response = self.client.post(self.get_url_param([self.division.id]), p, follow=True)
        self.assertEqual(response.status_code, 200)
        update_division = models.Division.objects.get(id=self.division.id)
        self.assertEqual(response.redirect_chain[0], ('/perm/division/%s/' % update_division.id, 302))
        self.assertEqual(p['name'], update_division.name)
        self.assertListEqual(p['employees'], list(update_division.employees.all().values_list('id', flat=True)))
        self.assertIn(p['full_access'], update_division.full_access.all().values_list('id', flat=True))
        self.assertIn(p['read_access'], update_division.read_access.all().values_list('id', flat=True))


class DivisionDeleteTest(BaseDivision):
    view_path = 'perm_division_delete'

    def test_403(self):
        self.division.full_access.clear()
        response = self.client.get(self.get_url_param([self.division.id]))
        self.assertEqual(response.status_code, 403)

    def test_200(self):
        self.division.full_access.add(self.division.id)
        response = self.client.get(self.get_url_param([self.division.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        self.division.full_access.add(self.division.id)
        response = self.client.post(self.get_url_param([self.division.id]), follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Division.objects.filter(id=self.division.id).count(), 0)