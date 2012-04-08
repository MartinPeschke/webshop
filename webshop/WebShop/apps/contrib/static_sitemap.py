from django.contrib.sitemaps import Sitemap

class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1

    def items(self):
        return ['aboutus', 'agb', 'news', 'downloads', 'materials', 'gallery', 'ourads', 'shipping', 'impressum', 'studios', 'agb', 'contact', 'seminar']

    def location(self, obj):
        return '/%s/' % obj