# coding: utf-8

class ListTestMixin(object):
    success_url = None

    def test_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

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
        self.empl.read_access.add(self.division)
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)    # FIXME

    def test_empty_object(self):
        self.empl.read_access.clear()
        self.empl.full_access.clear()
        response = self.client.get(self.get_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 0)