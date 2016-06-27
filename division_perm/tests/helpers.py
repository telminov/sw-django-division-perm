# coding: utf-8


class LoginRequiredTestMixin(object):

    def test_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403) # todo: страннова-то логичнее бы было редиректить на страницу логина


class ListAccessTestMixin(object): # todo: вынесла отдельно, т.к func нет такого поведения

    def test_empty_object(self):
        for obj in self.model_access.objects.all():
            obj.full_access.clear()
            obj.read_access.clear()
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['object_list'].count())


class ListTestMixin(LoginRequiredTestMixin):
    success_url = None
    model_access = None

    def test_no_roles(self):
        self.user.employee.roles.all().delete()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

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


class ReadAccessTestMixin(object):
    model_access = None

    def test_detail_403(self):
        for obj in self.model_access.objects.all():
            obj.full_access.clear()
            obj.read_access.clear()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)


class DetailTestMixin(LoginRequiredTestMixin):

    def test_200(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_instance(), response.context['object'])

