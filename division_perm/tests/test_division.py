# coding: utf-8
from .. import models
from ..views import division
from ..tests.base import BaseTest
from ..tests.helpers import ReadAccessTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, SortTestMixin, \
    ListAccessTestMixin, CreateTestMixin, UpdateTestMixin, DeleteTestMixin
from .. import factories


class ListTest(SortTestMixin, ListAccessTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_division_list'
    view_class = division.List
    factory_class = factories.Division


class DetailTest(ReadAccessTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_division_detail'
    view_class = division.Detail
    factory_class = factories.Division


class CreateTest(CreateTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_division_create'
    view_class = division.Create

    def get_create_data(self) -> dict:
        return {
            'name': 'test_created_division',
            'full_access': self.employee.get_default_division().id
        }


class UpdateTest(UpdateTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_division_update'
    view_class = division.Update
    factory_class = factories.Division

    def get_update_data(self) -> dict:
        return {
            'name': 'changed_division',
            'full_access': self.employee.get_default_division().id
        }

    def check_updated(self):
        division = models.Division.objects.get(id=self.get_instance().id)
        self.assertEqual(
            division.name,
            self.get_update_data()['name']
        )


class DeleteTest(DeleteTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_division_delete'
    view_class = division.Delete
    factory_class = factories.Division
