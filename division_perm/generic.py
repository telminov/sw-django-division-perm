# coding: utf-8
from django.contrib.auth.mixins import UserPassesTestMixin
from . import models


class CreateMainEntityMixin:

    def form_valid(self, form):
        response = super().form_valid(form)

        # если не определен доступ на изменение, то используем подразделение сотрудника
        if not self.object.full_access.exists():
            user_division = self.request.user.employee.get_default_division()
            self.object.full_access.add(user_division)

        return response


class FuncAccessMixin(UserPassesTestMixin):
    raise_exception = True
    func_code = ''

    def test_func(self):
        if not self.func_code:
            return True

        if not self.request.user.is_authenticated():
            return False

        # FIXME: не уверен что правильно - не учитываются подразделения ролей
        levels = [r.level for r in self.request.user.employee.roles.all()]
        if not levels:
            return False

        user_level = max(levels)
        func_level = models.Func.objects.get(code=self.func_code).level

        return func_level <= user_level


class ModifyAccessMixin(FuncAccessMixin):
    raise_exception = True

    def test_func(self):
        test_passed = super().test_func()
        if not test_passed:
            return False

        employee = self.request.user.employee
        employee_division = set(models.Division.objects.filter(employees=employee))
        access_divisions = self.get_access_divisions()

        have_access = bool(employee_division & access_divisions)
        return have_access

    def get_access_divisions(self) -> set:
        divisions = set()
        divisions.update(self.get_full_access_divisions())
        return divisions

    def get_full_access_divisions(self):
        qs = self.get_object().get_full_access()
        return qs


class ReadAccessMixin(ModifyAccessMixin):

    def get_access_divisions(self) -> set:
        divisions = super().get_access_divisions()
        divisions.update(self.get_only_read_access_divisions())
        return divisions

    def get_only_read_access_divisions(self):
        qs = self.get_object().get_only_read_access()
        return qs


class ListAccessMixin:
    main_entity_lookup = ''

    def get_queryset(self):
        return self.model.GetAccessible(self.request.user)


class FormAccessMixin:

    def get_initial(self):
        initial = super().get_initial()
        if not (self.object and self.object.id):
            initial['full_access'] = [self.request.user.employee.get_default_division()]
        return initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['user'] = self.request.user
        return form_kwargs

