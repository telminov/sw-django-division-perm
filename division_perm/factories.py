# coding: utf-8
import factory
import factory.fuzzy
from . import models


class Division(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Division

    name = factory.fuzzy.FuzzyText(length=15, prefix='test_division_')
