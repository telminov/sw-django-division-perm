# coding: utf-8
from .. import consts

from division_perm.tests.base import BaseTest
from division_perm.tests.helpers import *


class ListFuncTest(FuncAccessTestMixin, ListTestMixin, BaseTest):
    view_path = 'perm_func_list'
    success_url = reverse('perm_func_list') + '?sort=code'
    model_access = models.Func
    func_code = consts.SYS_READ_FUNC


class DetailFuncTest(FuncAccessTestMixin, DetailTestMixin, BaseTest):
    view_path = 'perm_func_detail'
    func_code = consts.SYS_READ_FUNC

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().id])
        return url

    def get_instance(self):
        func_read = models.Func.objects.get(code=consts.SYS_READ_FUNC)
        return func_read