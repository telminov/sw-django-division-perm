# coding: utf-8
from .. import consts

from division_perm.tests.base import BaseTest
from division_perm.tests.helpers import *

class BaseEmployee(BaseTest):
    view_path = None

    def get_params(self):
        division = models.Division.objects.all()[0]

        p = {
            'username': 'ivanov',
            'password1': 't1234567',
            'password2': 't1234567',
            'last_name': 'Ivanov',
            'first_name': 'Ivan',
            'middle_name': 'Ivanovich',
            'divisions': division.id,
            'full_access': division.id,
            'read_access': division.id,
            'is_active': True,
            'can_external': False,
        }
        return p


    def get_ident_emp_param(self):
        p = self.get_params()

        return {
            'user__username': p['username'],
            'last_name': p['last_name'],
            'middle_name': p['middle_name'],
            'first_name': p['first_name'],
            'divisions__id__in': [p['divisions']],
            'full_access__id__in': [p['full_access']],
            'read_access__id__in': [p['full_access']],
            'user__is_active': p['is_active'],
            'can_external': p['can_external'],
        }


class EmployeeListTest(FuncAccessTestMixin, ListTestMixin, ListAccessTestMixin, BaseEmployee):
    view_path = 'perm_employee_list'
    success_url = reverse('perm_employee_list') + '?sort=last_name'
    model_access = models.Employee
    func_code = consts.SYS_READ_FUNC


class EmployeeDetailTest(DetailTestMixin, ReadAccessTestMixin, BaseEmployee):
    view_path = 'perm_employee_detail'
    model_access = models.Employee

    def get_instance(self):
        return self.user.employee

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url


class EmployeeCreateTest(CreateTestMixin, BaseEmployee):
    view_path = 'perm_employee_create'
    model = models.Employee
    success_path = 'perm_employee_detail'
    exclude_fields = ['password1', 'password2', 'username', 'is_active']

    def get_ident_param(self):
        return self.get_ident_emp_param()


class EmployeeUpdateTest(UpdateTestMixin, ModifyAccessTestMixin, BaseEmployee):
    view_path = 'perm_employee_update'
    model = models.Employee
    success_path = 'perm_employee_detail'

    def get_instance(self):
        return self.user.employee

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url

    def get_ident_param(self):
       return self.get_ident_emp_param()


class EmployeeDeleteTest(DeleteTestMixin, BaseEmployee):
    view_path = 'perm_employee_delete'
    model = models.Employee

    def generate_data(self):
        self.other_empl = models.Employee.objects.exclude(id=self.user.employee.id)[0]

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url

    def get_instance(self):
        return self.other_empl


class EmployeePasswordChangeTest(UpdateTestMixin, ModifyAccessTestMixin,  BaseEmployee):
    view_path = 'perm_employee_password_change'
    model = models.Employee

    def get_instance(self):
        return self.user.employee

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url

    def get_params(self):
        return {
            'password1': 'new_password',
            'password2': 'new_password',
        }

    def test_update(self):
        old_password = self.get_instance().user.password

        response = self.client.post(self.get_url(), self.get_params(), follow=True)
        self.assertEqual(response.redirect_chain[0], ('..', 302))
        update_empl = models.Employee.objects.get(id=self.get_instance().id)
        self.assertNotEqual(update_empl.user.password, old_password)


class EmployeeRolesTest(UpdateTestMixin, ModifyAccessTestMixin, BaseEmployee):
    view_path = 'perm_employee_roles'
    model = models.Employee
    success_path = 'perm_employee_detail'

    def get_instance(self):
        return self.user.employee

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url

    def get_params(self):
        return {
            'user': self.get_instance().user,
            'roles': [self.get_instance().id],
        }

    def get_ident_param(self):
        p = self.get_params()

        return {
            'roles__id__in': p['roles'],
        }