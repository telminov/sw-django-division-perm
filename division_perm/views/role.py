# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from djutils.views.generic import TitleMixin
from .. import models
from .. import forms
from .. import consts
from ..generic import ReadAccessMixin, ModifyAccessMixin


class Create(TitleMixin, ModifyAccessMixin, LoginRequiredMixin, generic.CreateView):
    func_code = consts.SYS_EDIT_FUNC
    title = 'Регистрация роли'
    model = models.Role
    form_class = forms.Role
    success_url = '../..'

    def get_initial(self):
        initial = super().get_initial()
        initial['division'] = self.kwargs['division_pk']
        return initial

    def get_full_access_divisions(self):
        division = models.Division.objects.get(id=self.kwargs['division_pk'])
        return division.get_full_access()


class Detail(ReadAccessMixin, TitleMixin, LoginRequiredMixin, generic.DetailView):
    func_code = consts.SYS_READ_FUNC
    model = models.Role

    def get_title(self):
        return 'Роль "%s"' % self.get_object().name


class Update(TitleMixin, ModifyAccessMixin, LoginRequiredMixin, generic.UpdateView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Role
    form_class = forms.Role
    success_url = '../../..'

    def get_title(self):
        return 'Редактирование ролм "%s"' % self.get_object().name


class Delete(TitleMixin, ModifyAccessMixin, LoginRequiredMixin, generic.DeleteView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Role
    success_url = '../../..'
    template_name = 'core/base_delete.html'

    def get_title(self):
        return 'Удаление роли "%s"' % self.get_object().name
