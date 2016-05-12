# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from djutils.views.generic import TitleMixin
from ..generic import ListAccessMixin, FuncAccessMixin, ReadAccessMixin, ModifyAccessMixin, FormAccessMixin
from .. import models
from .. import forms
from .. import consts


class List(TitleMixin, FuncAccessMixin, ListAccessMixin, LoginRequiredMixin, generic.ListView):
    func_code = consts.SYS_READ_FUNC
    title = 'Подразделения'
    model = models.Division


class Detail(ReadAccessMixin, TitleMixin, LoginRequiredMixin, generic.DetailView):
    func_code = consts.SYS_READ_FUNC
    model = models.Division

    def get_title(self):
        return 'Подразделение "%s"' % self.get_object().name


class Create(TitleMixin, FormAccessMixin, LoginRequiredMixin, generic.CreateView):
    func_code = consts.SYS_EDIT_FUNC
    title = 'Регистрация подразделения'
    model = models.Division
    form_class = forms.Division


class Update(TitleMixin, FormAccessMixin, ModifyAccessMixin, LoginRequiredMixin, generic.UpdateView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Division
    form_class = forms.Division

    def get_title(self):
        return 'Редактирование подразделения "%s"' % self.get_object().name


class Delete(TitleMixin, ModifyAccessMixin, LoginRequiredMixin, generic.DeleteView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Division
    success_url = reverse_lazy('perm_division_list')
    template_name = 'core/base_delete.html'

    def get_title(self):
        return 'Удаление подразделения "%s"' % self.get_object().name
