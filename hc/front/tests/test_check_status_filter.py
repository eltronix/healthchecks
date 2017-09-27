from datetime import timedelta

from django.utils import timezone

from hc.api.models import Check
from hc.test import BaseTestCase


class CheckStatusFilterTestCase(BaseTestCase):
    def setUp(self):
        super(CheckStatusFilterTestCase, self).setUp()

        self.client.login(username="alice@example.org", password="password")

        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.last_ping = timezone.now()
        self.check.save()

    def test_it_works_without_filter(self):
        url = "/checks/"
        r = self.client.get(url)
        self.assertContains(r, "Alice Was Here", status_code=200)
        self.assertEquals(len(r.context["checks"]), 1)
        self.assertEquals(r.context["checks"][0].status, "new")

    def test_invalid_filter_fails_gracefully(self):
        urls = ["/checks/?status=invalid", "/checks/?stat=invalid", "/checks/?" ]

        for url in urls:
            r = self.client.get(url)
            self.assertEquals(len(r.context["checks"]), 1)

    def test_up_filter_works(self):
        self.check.status = "up"
        self.check.save()

        url = "/checks/?status=up"
        r = self.client.get(url)
        self.assertContains(r, "Alice Was Here", status_code=200)
        self.assertEquals(len(r.context["checks"]), 1)
        self.assertEquals(r.context["checks"][0].status, "up")

        # other views should be nil
        urls = ["/checks/?status=new", "/checks/?status=down", "/checks/?status=paused"]
        for url in urls:
            r = self.client.get(url)
            self.assertEquals(len(r.context["checks"]), 0)

    def test_paused_filter_works(self):
        self.check.status = "paused"
        self.check.save()

        url = "/checks/?status=paused"
        r = self.client.get(url)
        self.assertContains(r, "Alice Was Here", status_code=200)
        self.assertEquals(len(r.context["checks"]), 1)
        self.assertEquals(r.context["checks"][0].status, "paused")

        # other views should be nil
        urls = ["/checks/?status=new", "/checks/?status=down", "/checks/?status=up"]
        for url in urls:
            r = self.client.get(url)
            self.assertEquals(len(r.context["checks"]), 0)

    def test_down_filter_works(self):
        self.check.last_ping = timezone.now() - timedelta(days=2)
        self.check.status = "down"
        self.check.save()

        url = "/checks/?status=down"
        r = self.client.get(url)
        self.assertContains(r, "Alice Was Here", status_code=200)
        self.assertEquals(len(r.context["checks"]), 1)
        self.assertEquals(r.context["checks"][0].status, "down")

        # other views should be nil
        urls = ["/checks/?status=new", "/checks/?status=up", "/checks/?status=paused"]
        for url in urls:
            r = self.client.get(url)
            self.assertEquals(len(r.context["checks"]), 0)


