# coding: utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .. import models
from .. import consts


class BaseMixin:
    view_path = None    # ''
    view_class = None   #
    factory_class = None

    def setUp(self):
        super().setUp()
        self.generate_data()

    def get_url(self):
        url = reverse(self.view_path)
        return url

    def generate_data(self):
        self.user = User.objects.create_user(username='tester', email='tester@soft-way.biz', password='123')
        self.employee = models.Employee.objects.create(user=self.user, last_name=self.user.username)

        division = models.Division.objects.create(name='testing')
        division.employees.add(self.employee)
        division.full_access.add(division)

        func_read = models.Func.objects.get(code=consts.SYS_READ_FUNC)
        role = models.Role.objects.create(name='manager', code=func_read.code, level=9, division=division)
        self.employee.roles.add(role)

    def test_open_success(self):
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)


class LoginRequiredTestMixin(BaseMixin):

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password='123')

    def test_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)


class SortTestMixin(BaseMixin):

    def test_sort_redirect(self):
        if not (hasattr(self.view_class, 'sort_params') and self.view_class.sort_params):
            return

        sort_param = self.view_class.sort_params[0]
        sorted_url = reverse(self.view_path) + '?sort=' + sort_param
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0],
            (sorted_url, 302)
        )


class SingleObjectTestMixin(BaseMixin):

    def get_instance(self):
        if not hasattr(self, 'instance'):
            self.instance = self.factory_class()
        return self.instance

    def get_main_entity(self):
        instance = self.get_instance()
        if hasattr(self.view_class.model, 'main_entity_lookup') and self.view_class.model.main_entity_lookup:
            return getattr(instance, self.view_class.model.main_entity_lookup)
        else:
            return instance

    def get_url(self):
        url = reverse(self.view_path, args=[self.get_instance().pk])
        return url


class FuncAccessTestMixin(BaseMixin):

    def generate_data(self):
        super().generate_data()

        func, _ = models.Func.objects.get_or_create(
            code=self.view_class.func_code,
            defaults={'name': self.view_class.func_code, 'level': 5},
        )

        division = self.employee.divisions.all()[0]
        role = models.Role.objects.create(
            division=division,
            code='test_role',
            name='test_role',
            level=func.level,
        )
        role.employees.add(self.employee)

        self.employee = models.Employee.objects.get(id=self.employee.id)

    def test_role_level_must_be_greater_func_level(self):
        func = models.Func.objects.get(code=self.view_class.func_code)
        self.employee.roles.update(level=func.level-1)

        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 403)


class ModifyAccessTestMixin(SingleObjectTestMixin, BaseMixin):

    def generate_data(self):
        super().generate_data()
        division = self.employee.get_default_division()
        self.get_main_entity().full_access.add(division)

    def test_read_access_is_not_enough(self):
        self.get_main_entity().full_access.clear()
        division = self.employee.get_default_division()
        self.get_main_entity().read_access.add(division)
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 403)


class ListAccessTestMixin(BaseMixin):

    def generate_data(self):
        super().generate_data()
        division = self.employee.divisions.all()[0]
        other_division = models.Division.objects.create(name='other_division')

        objects = self.factory_class.create_batch(size=3)
        objects[0].full_access.add(division)
        objects[1].read_access.add(division)
        objects[2].full_access.add(other_division)

    def test_get_accessible(self):
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            sorted(list(response.context['object_list'].values_list('pk', flat=True))),
            sorted(list(self.view_class.model.GetAccessible(self.user).values_list('pk', flat=True)))
        )


class ReadAccessTestMixin(SingleObjectTestMixin, BaseMixin):

    def generate_data(self):
        super().generate_data()
        division = self.employee.divisions.all()[0]
        self.get_main_entity().read_access.add(division)

    def test_no_access(self):
        self.get_main_entity().read_access.clear()
        self.get_main_entity().full_access.clear()
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_read_available_for_full_access(self):
        self.get_main_entity().read_access.clear()
        division = self.employee.divisions.all()[0]
        self.get_main_entity().full_access.add(division)
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)


class CreateTestMixin(BaseMixin):

    def get_create_data(self) -> dict:
        raise NotImplementedError()

    def get_ident_param(self) -> dict:
        return self.get_create_data()

    def test_create(self):
        params = self.get_create_data()
        response = self.client.post(self.get_url(), params, follow=True)
        if 'form' in response.context:
            self.assertFalse(response.context['form'].errors)
        self.assertTrue(len(response.redirect_chain))
        self.assertTrue(self.view_class.model.objects.filter(**self.get_ident_param()).exists())


class UpdateTestMixin(ModifyAccessTestMixin, BaseMixin):

    def get_update_data(self) -> dict:
        raise NotImplementedError()

    def check_updated(self):
        raise NotImplementedError()

    def test_update(self):
        params = self.get_update_data()
        response = self.client.post(self.get_url(), params, follow=True)
        if 'form' in response.context:
            self.assertFalse(response.context['form'].errors)
        self.assertTrue(len(response.redirect_chain))
        self.check_updated()


class DeleteTestMixin(ModifyAccessTestMixin, BaseMixin):

    def test_delete(self):
        obj_id = self.get_instance().pk
        response = self.client.post(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.view_class.model.objects.filter(id=obj_id).exists())




# class CreateMainEntityTestMixin: # todo: from division_perm.generic.CreateMainEntityMixin -используется только в этом месте , но никогда не выполняется
#    pass
#
#
# class FormAccessTestMixin: # todo: надо подумать
#     pass
#
# class RestTestMixin: # todo: используется?
#     pass
#
# class RestNestedTestMixin: # todo: используется?
#     pass
