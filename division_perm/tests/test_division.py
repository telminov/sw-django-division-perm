# coding: utf-8
from .. import consts
from division_perm.tests.base import BaseTest
from division_perm.tests.helpers import *

class BaseDivisionTest(BaseTest):

    def get_params(self):
        division = models.Division.objects.all()[0]
        p = {
            'name': 'Managers',
            'employees': [self.user.employee.id],
            'full_access': division.id,
            'read_access': division.id,
        }
        return p

    def get_ident_param(self):
        p = self.get_params()

        return {
            'name': p['name'],
            'employees__id__in': p['employees'],
            'full_access__id__in': [p['full_access']],
            'read_access__id__in': [p['full_access']],
        }


class DivisionListTest(FuncAccessTestMixin, ListAccessTestMixin, ListTestMixin, BaseDivisionTest):
    view_path = 'perm_division_list'
    success_url = reverse('perm_division_list') + '?sort=name'
    model_access = models.Division
    func_code = consts.SYS_READ_FUNC


class DivisionDetailTest(ReadAccessTestMixin, DetailTestMixin, BaseDivisionTest):
    view_path = 'perm_division_detail'

    def get_instance(self):
        division = models.Division.objects.all()[0]
        return division

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url + '?role_sort=-level' # todo: возможно изменить логику тестового миксина


class DivisionCreateTest(CreateTestMixin, BaseDivisionTest):
    view_path = 'perm_division_create'
    model = models.Division
    success_path = 'perm_division_detail'


class DivisionUpdateTest(UpdateTestMixin, BaseDivisionTest):
    view_path = 'perm_division_update'
    model = models.Division
    success_path = 'perm_division_detail'

    def get_instance(self):
        return models.Division.objects.all()[0]

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url


class DivisionDeleteTest(DeleteTestMixin, BaseDivisionTest):
    view_path = 'perm_division_delete'
    model = models.Division

    def get_instance(self):
        return self.user.employee.divisions.filter(roles__code=consts.SYS_EDIT_FUNC)[0]

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url