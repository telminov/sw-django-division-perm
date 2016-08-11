# coding: utf-8

from django.test import TestCase
from django.contrib.auth.models import User

from division_perm import models
from division_perm import consts


class BaseModels(TestCase):
    fixtures = ['perm_func']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        self.employee = models.Employee.objects.create(user=self.user, last_name=self.user.username)
        self.division = models.Division.objects.create(name='testing')
        self.division2 = models.Division.objects.create(name='testing2')
        self.division.employees.add(self.employee)
        self.division.full_access.add(self.division)
        func_read = models.Func.objects.get(code=consts.SYS_READ_FUNC)
        self.role = models.Role.objects.create(name='manager', code=func_read.code, level=2, division=self.division)


class EmployeeTestCase(BaseModels):
    # def test_get_absolute_url(self):
    #     self.assertEqual(self.user.employee.get_absolute_url(), "/employee/%d/" % self.user.employee.id)

    def test_get_default_division(self):
        self.assertEqual(
            self.user.employee.get_default_division(),
            self.user.employee.divisions.all()[0]
        )

    def test_get_secret_key(self):
        key = "test_key"
        self.user.employee.set_secret_key(key)
        self.assertEqual(self.user.employee.get_secret_key(), key)

    def test_set_secret_key(self):
        secret_key = 'test_secret_key'
        self.user.employee.set_secret_key(secret_key)
        self.assertEqual(self.user.employee.get_secret_key(), secret_key)


# class DivisionTestCase(BaseModels):
#     def test_get_absolute_url(self):
#         self.assertEqual(self.division.get_absolute_url(), "/division/%d/" % self.division.id)


class RoleTestCase(BaseModels):
    def test_get_available_funcs(self):
        models.Func.objects.update(level=self.role.level)
        func_ids = models.Func.objects.values_list('id',  flat=True)
        self.assertListEqual(
            sorted(self.role.get_available_funcs().values_list('id',  flat=True)),
            sorted(func_ids)
        )

    def test_get_full_access(self):
        self.division.full_access.add(self.division)
        self.division.roles.add(self.role)
        self.assertIn(self.division, self.role.get_full_access())

    def test_get_only_read_access(self):
        self.division.read_access.add(self.division)
        self.division.roles.add(self.role)
        self.assertIn(self.division, self.role.get_only_read_access())


class AccessMixinTestCase(BaseModels):

    def test_getaccessible_without_result(self):
        self.employee.divisions.clear()
        results = models.Employee.GetAccessible(self.user)
        self.assertFalse(results)

    def test_getaccessible_with_full_access(self):
        self.employee.divisions.add(self.division)
        self.employee.full_access.add(self.division)
        self.assertIn(self.user.employee, models.Employee.GetAccessible(self.user))

    def test_getaccessible_with_read_access(self):
        self.employee.divisions.add(self.division)
        self.employee.read_access.add(self.division)
        self.assertIn(self.user.employee, models.Employee.GetAccessible(self.user))

    def test_getlookups(self):
        self.assertListEqual(models.Employee._GetLookups(), ['full_access__in', 'read_access__in'])

    def test_getlookups_for_model_role(self):
        main_entity_lookup = models.Role.main_entity_lookup
        self.assertListEqual(
            models.Role._GetLookups(),
            ['%s__full_access__in' % main_entity_lookup, '%s__read_access__in' % main_entity_lookup]
        )

    def test_get_full_access(self):
        self.employee.full_access.add(self.division)
        self.assertIn(self.division, models.Employee.get_full_access(self.employee))

    def test_get_full_access_is_empty(self):
        self.employee.full_access.clear()
        self.assertFalse(models.Employee.get_full_access(self.employee))

    def test_get_only_read_access(self):
        self.employee.read_access.add(self.division)
        self.assertIn(self.division, models.Employee.get_only_read_access(self.employee))

    def test_get_only_read_access_is_empty(self):
        self.employee.read_access.clear()
        self.assertFalse(models.Employee.get_only_read_access(self.employee))

    def test_get_read_access_only_read_access(self):
        self.employee.full_access.clear()
        self.employee.read_access.add(self.division)
        self.assertIn(self.division, models.Employee.get_read_access(self.employee))

    def test_get_read_access_only_full_access(self):
        self.employee.read_access.clear()
        self.employee.full_access.add(self.division)
        self.assertIn(self.division, models.Employee.get_read_access(self.employee))

    def test_get_read_access_is_empty(self):
        self.employee.read_access.clear()
        self.employee.full_access.clear()
        self.assertFalse(models.Employee.get_read_access(self.employee))

    def test_get_read_access_merge_full_and_read_access(self):
        self.employee.full_access.add(self.division)
        self.employee.read_access.add(self.division2)
        self.assertIn(self.division, models.Employee.get_read_access(self.employee))
        self.assertIn(self.division2, models.Employee.get_read_access(self.employee))

    def test_can_employee_modify_have_access(self):
        self.employee.divisions.add(self.division)
        self.employee.full_access.add(self.division)
        self.assertTrue(self.employee.can_employee_modify(self.employee))

    def test_can_employee_modify_have_not_access(self):
        self.employee.divisions.clear()
        self.employee.divisions.add(self.division2)
        self.employee.full_access.clear()
        self.employee.full_access.add(self.division)
        self.assertFalse(self.employee.can_employee_modify(self.employee))

    def test_can_employee_read_have_access(self):
        self.employee.divisions.add(self.division)
        self.employee.read_access.add(self.division)
        self.assertTrue(self.employee.can_employee_read(self.employee))

    def test_can_employee_read_have_not_access(self):
        self.employee.divisions.clear()
        self.employee.divisions.add(self.division2)
        self.employee.read_access.clear()
        self.employee.read_access.add(self.division)
        self.assertFalse(self.employee.can_employee_read(self.employee))