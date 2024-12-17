"""
"Smoke" tests to ensure that views load and templates render.
"""

from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(SITE_ID=1)
class SmokeTests(TestCase):
    fixtures = ["smoketest.json"]

    def test_homepage(self):
        response = self.client.get(reverse("home_page"))
        self.assertEqual(response.status_code, 200)
        # Custom home page for the site
        self.assertTemplateUsed(response, "veselosky.me/index.html")
        # Header template set by sitevar
        self.assertTemplateUsed(response, "storyville/blocks/header_masthead.html")
        # Filename is veseloksy.css, but it's delivered as veselosky.<hash>.css
        self.assertContains(
            response, 'link rel="stylesheet" href="/static/veselosky.me/veselosky.'
        )

    def test_sitemap(self):
        response = self.client.get(reverse("django.contrib.sitemaps.views.sitemap"))
        self.assertEqual(response.status_code, 200)

    def test_rss_feed(self):
        response = self.client.get(reverse("site_feed"))
        self.assertEqual(response.status_code, 200)

    def test_tinymce_image_list(self):
        response = self.client.get(reverse("tinymce_image_list"))
        self.assertEqual(response.status_code, 200)
        imglist = response.json()
        # 8 images in the fixture, view should return up to 10
        self.assertEqual(len(imglist), 8)
