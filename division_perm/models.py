# coding: utf-8
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class AccessMixin:
    main_entity_lookup = ''

    @classmethod
    def GetAccessible(cls, user: User):

        employee_division = user.employee.divisions.all()
        full_access_lookup, read_access_lookup = cls._GetLookups()

        qs = cls.objects.filter(Q(**{full_access_lookup: employee_division}) | Q(**{read_access_lookup: employee_division}))
        return qs.distinct()

    @classmethod
    def _GetLookups(cls):
        prefix = ''
        if cls.main_entity_lookup:
            prefix = cls.main_entity_lookup + '__'

        lookups = []
        for name in ['full_access', 'read_access']:
            lookups.append('%s%s__in' % (prefix, name))

        return lookups

    def get_full_access(self) -> models.QuerySet:
        return self.full_access.all()

    def get_only_read_access(self) -> models.QuerySet:
        return self.read_access.all()

    def get_read_access(self) -> models.QuerySet:
        division_ids = set()
        division_ids.update(self.get_full_access().values_list('id', flat=True))
        division_ids.update(self.get_only_read_access().values_list('id', flat=True))
        read_access = Division.objects.filter(id__in=division_ids)
        return read_access


class Employee(AccessMixin, models.Model):
    user = models.OneToOneField(User, related_name='employee')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    first_name = models.CharField(max_length=255, verbose_name='Имя', blank=True)
    middle_name = models.CharField(max_length=255, verbose_name='Отчество', blank=True)
    roles = models.ManyToManyField('Role', verbose_name='Роли', related_name='employees')

    full_access = models.ManyToManyField('Division', related_name='owners', verbose_name='Полный доступ')
    read_access = models.ManyToManyField('Division', related_name='readers', verbose_name='Доступ на чтение', blank=True)

    class Meta:
        unique_together = ('last_name', 'first_name', 'middle_name')

    def __str__(self):
        return ' '.join(filter(bool, (self.last_name, self.first_name, self.middle_name)))

    def get_absolute_url(self):
        return reverse('perm_employee_detail', kwargs={'pk': self.id})

    def get_default_division(self):
        return self.divisions.first()


class Division(AccessMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name='Название', unique=True)
    employees = models.ManyToManyField(Employee, related_name='divisions', verbose_name='Сотрудники', blank=True)

    full_access = models.ManyToManyField('self', related_name='owners', verbose_name='Полный доступ')
    read_access = models.ManyToManyField('self', related_name='readers', verbose_name='Доступ на чтение', blank=True)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('perm_division_detail', kwargs={'pk': self.id})


class Func(models.Model):
    code = models.CharField('Код', max_length=50, unique=True)
    name = models.CharField('Название', max_length=255, unique=True)
    description = models.TextField('Описание', blank=True)
    level = models.IntegerField('Уровень', default=0, help_text='0 - минимальный уровень доступа, 9 - максимальный')
    is_modify = models.BooleanField('Изменяет', default=False,
                                    help_text='Использование функции может быть связано с изменением данных')

    class Meta:
        verbose_name = 'Функция'
        verbose_name_plural = 'Функции'
        ordering = ('-level', 'name')

    def __str__(self):
        return self.name


class Role(AccessMixin, models.Model):
    main_entity_lookup = 'division'

    division = models.ForeignKey(Division, related_name='roles', verbose_name='Подразделение')
    code = models.CharField('Код', max_length=50, unique=True)
    name = models.CharField('Название', max_length=255, unique=True)
    description = models.TextField('Описание', blank=True)
    level = models.IntegerField('Уровень', default=0, help_text='0 - минимальный уровень доступа, 9 - максимальный')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ('division', '-level', 'name')

    def __str__(self):
        return self.name

    def get_available_funcs(self):
        return Func.objects.filter(level__lte=self.level)

    def get_full_access(self) -> models.QuerySet:
        return self.division.full_access.all()

    def get_only_read_access(self) -> models.QuerySet:
        return self.division.read_access.all()
