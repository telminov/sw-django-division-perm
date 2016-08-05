# coding: utf-8

from django.test import TestCase
from django.template import Context
from django.contrib.auth.models import User

from division_perm import models
from division_perm.templatetags.perm import can_modify, can_func, block_super_if_can_func

from unittest.mock import Mock


class BaseTemplatetagsTest(TestCase):
    fixtures = ['perm_func']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        self.employee = models.Employee.objects.create(user=self.user, last_name=self.user.username)
        self.division = models.Division.objects.create(name='testing')
        self.division2 = models.Division.objects.create(name='testing2')
        self.func = models.Func.objects.all()[0]
        self.role = models.Role.objects.create(name='manager', code=self.func.code, level=2, division=self.division)


class CanModifyFilterTest(BaseTemplatetagsTest):

    def test_can_modify_have_access(self):
        self.employee.divisions.add(self.division)
        self.employee.full_access.add(self.division)
        have_access = can_modify(self.employee, self.user)
        self.assertTrue(have_access)

    def test_can_modify_have_not_access(self):
        self.employee.divisions.clear()
        self.employee.full_access.clear()
        have_access = can_modify(self.employee, self.user)
        self.assertFalse(have_access)


class CanFuncTagTest(BaseTemplatetagsTest):

    def test_can_func_with_obj_and_is_modify_and_can_modify_is_false(self):
        self.func.is_modify = 1
        self.func.save()
        context = {'user': self.user}
        have_access = can_func(context, self.func.code, self.employee)
        self.assertFalse(can_modify(self.employee, self.user))
        self.assertFalse(have_access)

    def test_can_func_with_obj_and_is_modify_and_can_modify_is_true_and_user_level_gt_func_level(self):
        self.func.is_modify = 1
        self.func.save()
        context = {'user': self.user}
        self.employee.divisions.add(self.division)
        self.employee.full_access.add(self.division)
        self.employee.roles.add(self.role)
        self.assertFalse(self.func.level <= self.role.level)
        self.role.level = self.func.level + 2
        self.role.save()
        self.assertTrue(self.func.level <= self.role.level)
        have_access = can_func(context, self.func.code, self.employee)
        self.assertTrue(can_modify(self.employee, self.user))
        self.assertTrue(have_access)

    def test_can_func_with_obj_and_is_modify_is_false_and_user_level_lt_func_level(self):
        context = {'user': self.user}
        self.func.is_modify = 0
        self.func.save()
        self.assertFalse(can_modify(self.employee, self.user))
        self.employee.divisions.add(self.division)
        self.employee.read_access.add(self.division)
        self.employee.roles.add(self.role)
        self.assertFalse(self.func.level <= self.role.level)
        self.role.level = self.func.level - 2
        self.role.save()
        self.assertFalse(self.func.level <= self.role.level)
        have_access = can_func(context, self.func.code, self.employee)
        self.assertFalse(have_access)

    def test_can_func_with_obj_is_none(self):
        context = {'user': self.user}
        self.employee.divisions.add(self.division)
        have_access = can_func(context, self.func.code, self.employee)
        self.assertFalse(have_access)


class BlockSuperIfCanFuncTagTest(BaseTemplatetagsTest):

    def test_block_super_if_can_func(self):
        mock_block = Mock()
        mock_block.super = 'super'

        self.func.is_modify = 0
        self.func.save()
        self.employee.divisions.add(self.division)
        self.employee.read_access.add(self.division)
        self.employee.roles.add(self.role)
        self.assertFalse(self.func.level <= self.role.level)
        self.role.level = self.func.level + 2
        self.role.save()
        context = Context({'user': self.user, 'block': mock_block})
        result = block_super_if_can_func(context, self.func.code, self.employee)
        self.assertEqual(result['content'], context['block'].super)
        self.assertEqual(
            result['user_can_func'],
            can_func(Context({'user': self.user}), self.func.code, self.employee)
        )