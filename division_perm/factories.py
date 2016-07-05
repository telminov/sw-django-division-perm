# coding: utf-8
import factory
import factory.fuzzy
from . import models


class Division(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Division

    name = factory.fuzzy.FuzzyText(length=15, prefix='test_division_')


class Func(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Func

    name = factory.fuzzy.FuzzyText(length=15, prefix='test_func_')


class Role(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Role

    division = factory.SubFactory(Division)
    code = factory.fuzzy.FuzzyText(length=15, prefix='test_role_code_')
    name = factory.fuzzy.FuzzyText(length=15, prefix='test_role_name_')


class User(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = factory.fuzzy.FuzzyText(length=15, prefix='test_user_')


class Employee(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Employee

    user = factory.SubFactory(User)
    last_name = factory.fuzzy.FuzzyText(length=15, prefix='test_employee_')

    @classmethod
    def _prepare(cls, create, **kwargs):
        role = Role(level=9)
        employee = super(Employee, cls)._prepare(create, **kwargs)
        employee.roles.add(role)
        return employee
