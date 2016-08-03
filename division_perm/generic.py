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
        employee_divisions = set(models.Division.objects.filter(employees=employee))
        access_divisions = self.get_access_divisions()

        have_access = bool(employee_divisions & access_divisions)
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
        if not (self.object and self.object.pk):
            initial['full_access'] = [self.request.user.employee.get_default_division()]
        return initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['user'] = self.request.user
        return form_kwargs


class RestMixin(ListAccessMixin):
    def perform_create(self, serializer):
        super().perform_create(serializer)

        if hasattr(serializer.instance, 'full_access'):
            serializer.instance.full_access.add(self.request.user.employee.get_default_division())


class RestNestedMixin(RestMixin):
    main_model = None
    main_lookup = None

    def get_main_pk(self):
        return self.kwargs[self.main_lookup + '_pk']

    def filter_queryset(self, queryset):
        params = {self.main_lookup + '__pk': self.get_main_pk()}
        return queryset.filter(**params)

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            main_instance = self.main_model.objects.get(pk=self.get_main_pk())
            instance_params = {self.main_lookup: main_instance}
            kwargs['instance'] = self.model(**instance_params)
        return super().get_serializer(*args, **kwargs)
