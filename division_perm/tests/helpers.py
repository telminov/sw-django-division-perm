# coding: utf-8
from django.core.urlresolvers import reverse

from division_perm.generic import CreateMainEntityMixin
from division_perm import models

class CreateMainEntityTestMixin(object): # CreateMainEntityMixin -используется только в этом месте , но никогда не выполняется
   pass

class FuncAccessTestMixin(object):

    def test_without_func_code(self): # todo: избыточный код, везде есть func_code
        pass

    def test_no_is_authenticated(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)  # todo: избыточный код, везде есть LoginRequiredMixin

    def test_without_level(self):
        self.user.employee.roles.all().delete()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_priority_func_level(self):
        self.user.employee.roles.all().update(level=5)
        models.Func.objects.filter(code=self.func_code).update(level=10)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_priority_user_level(self):
        self.user.employee.roles.all().update(level=10)
        models.Func.objects.filter(code=self.func_code).update(level=5)
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0],
            (self.success_url, 302)
        )

class ModifyAccessTestMixin(object):

    def test_without_passed(self):
        models.Func.objects.all().update(level=10)
        self.user.employee.roles.all().update(level=5)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_with_have_access(self):
        self.user.employee.roles.all().update(level=10)
        models.Func.objects.all().update(level=10)
        division = self.user.employee.divisions.all()[0]
        self.get_instance().full_access.add(division)

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_without_have_access(self):
        self.user.employee.roles.all().update(level=10)
        models.Func.objects.all().update(level=10)
        self.get_instance().full_access.clear()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)


class ReadAccessTestMixin(object):

    def test_access_divisions(self):
        division = models.Division.objects.all()[0]
        self.get_instance().read_access.add(division)

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_instance(), response.context['object'])

    def test_without_access_divisions(self):
        self.get_instance().read_access.clear()
        self.get_instance().full_access.clear()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)


class ListAccessTestMixin(object): # todo: вынесла отдельно, т.к func нет такого поведения

    def test_get_queryset(self):
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context['object_list'].values_list('id', flat=True)),
            list(self.model_access.GetAccessible(self.user).values_list('id', flat=True))
        )


class FormAccessTestMixin(object): # todo: надо подумать
    pass

class RestTestMixin(object): # todo: используется?
    pass

class RestNestedTestMixin(object): # todo: используется?
    pass


class LoginRequiredTestMixin(object):

    def test_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403) # todo: страннова-то логичнее бы было редиректить на страницу логина


class ListTestMixin(LoginRequiredTestMixin):
    success_url = None
    model_access = None
    func_code = None

    def test_200(self):
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0],
            (self.success_url, 302)
        )

    def test_object(self):
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['object_list'].count(),
            self.model_access.objects.all().count()
        )


class DetailTestMixin(LoginRequiredTestMixin, ReadAccessTestMixin):
    model_access = None

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_instance(), response.context['object'])

