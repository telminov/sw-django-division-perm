# coding: utf-8
from django.core.urlresolvers import reverse

from .. import models
from ..views import role
from ..tests.base import BaseTest
from ..tests.helpers import ReadAccessTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, \
    CreateTestMixin, UpdateTestMixin, DeleteTestMixin
from .. import factories


class DetailTest(ReadAccessTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_role_detail'
    view_class = role.Detail
    factory_class = factories.Role

    def get_url(self):
        instance = self.get_instance()
        return reverse(self.view_path, kwargs={'division_pk': instance.division.id, 'pk': instance.id})


class CreateTest(CreateTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_role_create'
    view_class = role.Create

    def get_create_data(self) -> dict:
        return {
            'division': self.employee.get_default_division().id,
            'code': 'test_code',
            'name': 'test_name',
            'description': '123',
            'level': 1,
        }

    def get_url(self):
        return reverse(self.view_path, kwargs={'division_pk': self.employee.get_default_division().id})


class UpdateTest(UpdateTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_role_update'
    view_class = role.Update
    factory_class = factories.Role

    def get_update_data(self) -> dict:
        return {
            'division': self.employee.get_default_division().id,
            'code': 'test_code2',
            'name': 'test_name2',
            'description': '321',
            'level': 2,
        }

    def check_updated(self):
        role = models.Role.objects.get(id=self.get_instance().id)
        self.assertEqual(role.code, self.get_update_data()['code'])
        self.assertEqual(role.name, self.get_update_data()['name'])
        self.assertEqual(role.description, self.get_update_data()['description'])
        self.assertEqual(role.level, self.get_update_data()['level'])

    def get_url(self):
        instance = self.get_instance()
        return reverse(self.view_path, kwargs={'division_pk': instance.division.id, 'pk': instance.id})


class DeleteTest(DeleteTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_role_delete'
    view_class = role.Delete
    factory_class = factories.Role

    def get_url(self):
        instance = self.get_instance()
        return reverse(self.view_path, kwargs={'division_pk': instance.division.id, 'pk': instance.id})
