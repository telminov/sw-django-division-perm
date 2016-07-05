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
