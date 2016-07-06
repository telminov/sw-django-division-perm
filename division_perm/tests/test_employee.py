# coding: utf-8

from ..views import employee
from ..tests.base import BaseTest
from ..tests.helpers import *
from .. import factories


class BaseEmployeeTest(BaseTest):
    view_path = None

    def get_update_params(self):
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
        p = self.get_update_params()

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


class EmployeeListTest(SortTestMixin, ListAccessTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseEmployeeTest):
    view_path = 'perm_employee_list'
    view_class = employee.List
    factory_class = factories.Employee


class EmployeeDetailTest(ReadAccessTestMixin, LoginRequiredTestMixin, BaseEmployeeTest):
    view_path = 'perm_employee_detail'
    view_class = employee.Detail
    factory_class = factories.Employee


class EmployeeCreateTest(CreateTestMixin, LoginRequiredTestMixin, FuncAccessTestMixin, BaseEmployeeTest):
    view_path = 'perm_employee_create'
    view_class = employee.Create

    def get_create_data(self) -> dict:
        return self.get_update_params()

    def get_ident_param(self) -> dict:
        return self.get_ident_emp_param()


class EmployeeUpdateTest(UpdateTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseEmployeeTest):
    view_path = 'perm_employee_update'
    view_class = employee.Update
    factory_class = factories.Employee

    def get_update_data(self) -> dict:
        return self.get_update_params()

    def check_updated(self):
        self.assertTrue(
            models.Employee.objects.get(
                id=self.get_instance().id,
                **self.get_ident_emp_param()
            )
        )


class EmployeeDeleteTest(LoginRequiredTestMixin, DeleteTestMixin, BaseEmployeeTest):
    view_path = 'perm_employee_delete'
    view_class = employee.Delete
    factory_class = factories.Employee

    def generate_data(self):
        BaseMixin.generate_data(self)
        other_user = User.objects.create_user(username='tester_other', email='other_tester@soft-way.biz', password='123')
        other_employee = models.Employee.objects.create(user=other_user, last_name='other_test', first_name='test', middle_name='test')
        other_employee.full_access.add(self.employee.get_default_division())

    def get_instance(self):
        other_employee = models.Employee.objects.exclude(id=self.user.employee.id)[0]
        return other_employee


class EmployeePasswordChangeTest(LoginRequiredTestMixin, UpdateTestMixin, BaseEmployeeTest):
    view_path = 'perm_employee_password_change'
    view_class = employee.Update
    factory_class = factories.Employee

    def get_update_data(self) -> dict:
        return {
            'password1': 'new_password',
            'password2': 'new_password',
        }

    def test_update(self):
        old_password = self.get_instance().user.password

        response = self.client.post(self.get_url(), self.get_update_data(), follow=True)
        self.assertEqual(response.redirect_chain[0], ('..', 302))
        update_empl = models.Employee.objects.get(id=self.get_instance().id)
        self.assertNotEqual(update_empl.user.password, old_password)


class EmployeeRolesTest(UpdateTestMixin, LoginRequiredTestMixin, BaseEmployeeTest):
    view_path = 'perm_employee_roles'
    view_class = employee.Update
    factory_class = factories.Employee

    def get_update_data(self):
        division = self.employee.divisions.all()[0]
        role = models.Role.objects.get_or_create(
            name='test_new_role', code='test_code',
            level=9, division=division
        )[0]
        employee = self.get_instance()
        employee.divisions.add(division)

        return {
            'user': employee.user,
            'roles': role.id,
        }

    def check_updated(self):
        p = self.get_update_data()
        employee = models.Employee.objects.get(id=self.get_instance().id)
        self.assertIn(
            p['roles'],
            employee.roles.all().values_list('id', flat=True)
        )