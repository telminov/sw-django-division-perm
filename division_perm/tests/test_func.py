# coding: utf-8
from ..views import func
from ..tests.base import BaseTest
from ..tests.helpers import *
from .. import factories


class ListFuncTest(SortTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_func_list'
    view_class = func.List
    factory_class = factories.Func


class DetailFuncTest(SingleObjectTestMixin, FuncAccessTestMixin, LoginRequiredTestMixin, BaseTest):
    view_path = 'perm_func_detail'
    view_class = func.Detail
    factory_class = factories.Func