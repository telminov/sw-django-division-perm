# coding: utf-8
import datetime
from django.core.urlresolvers import reverse
import django.db.models

from division_perm import models

class CreateMainEntityTestMixin(object): # todo: from division_perm.generic.CreateMainEntityMixin -используется только в этом месте , но никогда не выполняется
   pass

class FuncAccessTestMixin(object):

    def test_without_func_code(self): # todo: избыточный код, везде в функциях есть func_code
        pass

    def test_no_is_authenticated(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)  # todo: избыточный код, везде есть LoginRequiredMixin зачем доп. проверка?

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
        if hasattr(self, 'success_url'):
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


class ListAccessTestMixin(object):

    def test_get_queryset(self):
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            sorted(list(response.context['object_list'].values_list('id', flat=True))),
            sorted(list(self.model_access.GetAccessible(self.user).values_list('id', flat=True)))
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
        response = self.client.get(self.get_url(),follow=True)
        if response.status_code == 302:
            self.assertIn('login/?next', response.redirect_chain[0][0]) # todo:  в случае с create
        else:
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


class DetailTestMixin(LoginRequiredTestMixin):
    model_access = None

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_instance(), response.context['object'])


class CreateTestMixin(object):
    view_path = 'perm_employee_create'
    models = None
    success_path = None

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        params = self.get_params()
        response = self.client.post(self.get_url(), params, follow=True)
        if 'form' in response.context:
            self.assertFalse(response.context['form'].errors)
        self.assertTrue(len(response.redirect_chain))
        created_obj = self.model.objects.filter(**self.get_ident_param())[0]
        success_url = reverse(self.success_path, args=[created_obj.id])
        self.assertEqual(response.redirect_chain[0], (success_url, 302))


class UpdateTestMixin(CreateTestMixin):

    def test_update(self):
        params = self.get_params()
        response = self.client.post(self.get_url(), params, follow=True)
        if 'form' in response.context:
            self.assertFalse(response.context['form'].errors)
        self.assertTrue(len(response.redirect_chain))
        update_obj = self.model.objects.get(id=self.get_instance().id, **self.get_ident_param())
        success_url = reverse(self.success_path, args=[update_obj.id])
        self.assertEqual(response.redirect_chain[0], (success_url, 302))


class DeleteTestMixin(LoginRequiredTestMixin, ModifyAccessTestMixin):
    model = None

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        obj_id = self.get_instance().id
        response = self.client.post(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.model.objects.filter(id=obj_id).count(), 0)