# coding: utf-8
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.views import generic
from djutils.views.generic import TitleMixin, SortMixin
from .. import models
from .. import consts
from .. import forms
from ..generic import CreateMainEntityMixin, ListAccessMixin, ReadAccessMixin, ModifyAccessMixin, FormAccessMixin, \
    FuncAccessMixin


class List(SortMixin, TitleMixin, FuncAccessMixin, ListAccessMixin, LoginRequiredMixin, generic.ListView):
    func_code = consts.SYS_READ_FUNC
    title = 'Сотрудники'
    model = models.Employee
    sort_params = ('last_name', )


class Detail(TitleMixin, ReadAccessMixin, LoginRequiredMixin, generic.DetailView):
    func_code = consts.SYS_READ_FUNC
    model = models.Employee

    def get_title(self):
        return 'Сотрудник "%s"' % self.get_object()


class Create(CreateMainEntityMixin, FormAccessMixin, TitleMixin, LoginRequiredMixin, generic.CreateView):
    func_code = consts.SYS_EDIT_FUNC
    title = 'Регистрация сотрудника'
    model = models.Employee
    form_class = forms.EmployeeCreate

    def get_success_url(self):
        return reverse('perm_employee_detail', kwargs={'pk': self.object.id})


class Update(TitleMixin, FormAccessMixin, ModifyAccessMixin, LoginRequiredMixin, generic.UpdateView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Employee
    form_class = forms.Employee

    def get_title(self):
        return 'Редактирование сотрудника "%s"' % self.get_object()


class Delete(TitleMixin, ModifyAccessMixin, LoginRequiredMixin, generic.DeleteView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Employee
    success_url = reverse_lazy('perm_employee_list')
    template_name = 'core/base_delete.html'

    def get_title(self):
        return 'Удаление сотрудника "%s"' % self.get_object()

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        self.object.user.delete()
        return response


class PasswordChange(TitleMixin, ModifyAccessMixin, LoginRequiredMixin, generic.UpdateView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Employee
    title = 'Изменение пароля'
    form_class = AdminPasswordChangeForm
    template_name = 'perm/employee_password_change.html'
    success_url = '..'

    def get_form_kwargs(self):
        form_kwargs = {
            'user': self.object.user,
            'data': self.request.POST or None,
        }
        return form_kwargs


class Roles(TitleMixin, ModifyAccessMixin, LoginRequiredMixin, generic.UpdateView):
    func_code = consts.SYS_EDIT_FUNC
    model = models.Employee
    form_class = forms.EmployeeRoles

    def get_title(self):
        return 'Роли сотрудника "%s"' % self.get_object()

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['user'] = self.request.user
        return form_kwargs

