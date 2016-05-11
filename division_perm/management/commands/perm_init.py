# coding: utf-8
import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ... import models


class Command(BaseCommand):
    help = 'Инициализация системы прав'

    def handle(self, *args, **options):
        # подразделение система
        sys_division, _ = models.Division.objects.get_or_create(name='Система')
        # полные права самой на себя
        models.Division.full_access.through.objects.get_or_create(from_division=sys_division, to_division=sys_division)

        # роль "Администратор"
        admin_role, _ = models.Role.objects.get_or_create(division=sys_division, code='admin', name='Администратор',
                                                          level=9)

        # пользователь superadmin
        admin_login = 'superadmin'
        if not models.Employee.objects.filter(user__username=admin_login).exists():
            password1 = password2 = None
            while not (password1 and password2 and password1 == password2):
                password1 = getpass.getpass('Input superadmin user password: ')
                password2 = getpass.getpass('Retype password: ')
                if password1 != password2:
                    print('Passwords dose not match.')

            user = User.objects.create_superuser(admin_login, '', password1, last_name='Администратор')
            models.Employee.objects.create(user=user, last_name=user.last_name)

        # привяжем его к подразделения Система
        superadmin = models.Employee.objects.get(user__username=admin_login)
        superadmin.full_access.add(sys_division)
        sys_division.employees.add(superadmin)

        # добавим роль Администратор
        superadmin.roles.add(admin_role)
