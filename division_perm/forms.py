# coding: utf-8
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core import validators

from . import models


class AccessMixin:
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['full_access'].queryset = models.Division.GetAccessible(user).order_by('name')
        self.fields['full_access'].help_text = 'Подразделения, которые будут иметь полный доступ к записи'

        self.fields['read_access'].queryset = models.Division.GetAccessible(user).order_by('name')
        self.fields['read_access'].help_text = 'Подразделения, которые будут иметь доступ к записи на чтение'


class EmployeeDivision(forms.ModelForm):
    divisions = forms.ModelMultipleChoiceField(
        label='Подразделения',
        queryset=models.Division.objects.none(),
        help_text='Подразделения, в которые входит сотрудник',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        employee_divisions = self.user.employee.divisions.all()
        self.fields['divisions'].queryset = models.Division.objects.filter(
            Q(full_access__in=employee_divisions) | Q(read_access__in=employee_divisions)
        ).order_by('name').distinct()

        if self.instance.id:
            self.fields['divisions'].initial = self.instance.divisions.all()

    def save(self, commit=True):
        employee = super().save(commit=commit)

        if commit:
            current_divisions = set(employee.divisions.all())
            new_divisions = set(self.cleaned_data['divisions'])

            deleted_divisions = current_divisions - new_divisions
            for division in deleted_divisions:
                division.employees.remove(employee)

            added_divisions = new_divisions - current_divisions
            for division in added_divisions:
                division.employees.add(employee)

        return employee


class EmployeeUser(forms.ModelForm):
    username = forms.CharField(
        label='Логин',
        max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ],
    )
    is_active = forms.BooleanField(label='Активен', required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['username'].initial = self.instance.user.username
            self.fields['is_active'].initial = self.instance.user.is_active

    def save(self, commit=True):
        employee = super().save(commit=commit)

        if commit:
            self.instance.user.username = self.cleaned_data['username']
            self.instance.user.is_active = self.cleaned_data['is_active']
            self.instance.user.save()
        return employee


class EmployeeCreate(EmployeeDivision, EmployeeUser, AccessMixin, forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = forms.CharField(label=_("Password"),
        strip=False,
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."))


    class Meta:
        model = models.Employee
        fields = ['username', 'password1', 'password2', 'last_name', 'first_name', 'middle_name',
                  'divisions', 'full_access', 'read_access', 'is_active']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            first_name=' '.join(filter(bool, (self.cleaned_data['first_name'], self.cleaned_data['middle_name']))),
            last_name=self.cleaned_data['last_name'],
            is_staff=False,
            is_active=True,
        )
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        self.instance.user = user
        employee = super().save(commit=True)
        return employee


class Employee(EmployeeDivision, EmployeeUser, AccessMixin, forms.ModelForm):
    class Meta:
        model = models.Employee
        fields = ['username', 'last_name', 'first_name', 'middle_name', 'divisions', 'full_access', 'read_access',
                  'is_active']


class EmployeeRoles(forms.ModelForm):
    roles = forms.MultipleChoiceField(label='Роль', required=False)

    class Meta:
        model = models.Employee
        fields = ['roles']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.user = user

        choices = []
        for division in self.instance.divisions.order_by('name'):
            for role in division.roles.all():
                choice = (role.id, "%s - %s" % (division.name, role.name))
                choices.append(choice)
        self.fields['roles'].choices = choices


class Division(AccessMixin, forms.ModelForm):
    class Meta:
        model = models.Division
        fields = ['name', 'employees', 'full_access', 'read_access']

    # из-за непонятной особенности (баги?) добавлять как прямое отношение так и обратное
    # при вызове метода add() у m2m-поля указывающего на модель 'self
    # использую не миксин CreateMainEntityMixin, а явное создание отношения через models.Division.full_access.through
    def save(self, commit=True):
        is_new = not self.instance.id
        full_access = self.cleaned_data.pop('full_access')
        read_access = self.cleaned_data.pop('read_access')

        division = super().save(commit=commit)

        if commit:
            models.Division.full_access.through.objects.filter(from_division=division).delete()
            for full_division in full_access:
                models.Division.full_access.through.objects.create(from_division=division, to_division=full_division)

            models.Division.read_access.through.objects.filter(from_division=division).delete()
            for read_division in read_access:
                models.Division.read_access.through.objects.create(from_division=division, to_division=read_division)

            # добавим доступ на чтение самой себе
            if is_new:
                models.Division.read_access.through.objects.create(from_division=division, to_division=division)

        return division


class Role(forms.ModelForm):
    employees = forms.ModelMultipleChoiceField(
        label='Сотрудники',
        queryset=models.Employee.objects.none(),
        required=False,
    )

    class Meta:
        model = models.Role
        fields = ['division', 'code', 'name', 'description', 'level', 'employees']
        widgets = {
            'division': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['employees'].initial = self.instance.employees.all()
            division = self.instance.division
        else:
            division = models.Division.objects.get(id=self.initial['division'])
        self.fields['employees'].queryset = division.employees.all()

    def save(self, commit=True):
        role = super().save(commit=commit)

        if commit:
            current_employees = set(self.instance.employees.all())
            new_employees = set(self.cleaned_data['employees'])

            deleted_employees = current_employees - new_employees
            for employee in deleted_employees:
                role.employees.remove(employee)

            added_employees = new_employees - current_employees
            for employee in added_employees:
                role.employees.add(employee)

        return role
