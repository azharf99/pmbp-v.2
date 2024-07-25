from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return ["ekskul:data-index", "laporan:laporan-index", "about", "license"]

    def location(self, item):
        return reverse(item)