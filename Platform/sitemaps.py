from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return ["extracurricular-list", "report-list", "prestasi-list", "nilai-list", "olympiad-report-list", "program-prestasi-list", "license"]

    def location(self, item):
        return reverse(item)