from django.conf import settings
from django_webtest import WebTest
from django.core.urlresolvers import reverse
from accounts.tests.factories import SuperUserFactory


class InterceptionRecordCreateViewTests(WebTest):

    def test_old_irf_route_redirects_to_client(self):
        self.superuser = SuperUserFactory.create()
        url = reverse("interceptionrecord_list")
        response = self.app.get(url, user=self.superuser)

        self.assertEquals(response.url, settings.CLIENT_DOMAIN + '/irf')

    def test_old_vif_route_redirects_to_client(self):
        self.superuser = SuperUserFactory.create()
        url = reverse("victiminterview_list")
        response = self.app.get(url, user=self.superuser)

        self.assertEquals(response.url, settings.CLIENT_DOMAIN + '/vif')