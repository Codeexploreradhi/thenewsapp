
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from newsfeed import views as newsviews

from speciousnews.sitemaps import SpeciousNewsSitemap
from django.contrib.sites.models import Site

_hostname = 'localhost:8000'

sitemaps = {
    'news': SpeciousNewsSitemap()
}

urlpatterns = [
    url(r'^sitemap\.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots\.txt', include('robots.urls')),
    url(r'^$', newsviews.show_news_topics),
    url(r'^topics/(?P<topic_id>\d+)$', newsviews.show_articles_by_topic, name="news_topics"),
    url(r'^keywords/$', newsviews.show_news_keywords),
    url(r'^keywords/(?P<keyword_id>\d+)$', newsviews.show_articles_by_keyword, name="news_keywords"),
    url(r'^about/$', newsviews.show_about_page),
    url(r'^about/graph/$', newsviews.show_cluster_graph),
    url(r'^search/$', newsviews.show_search_results),
    url(r'^sources/$', newsviews.show_counts_by_source),
    url(r'^admin/', admin.site.urls),
]

handler400 = newsviews.bad_request
handler403 = newsviews.forbidden_resource
handler404 = newsviews.page_not_found
handler500 = newsviews.server_error

try:
    _sites = Site.objects.all()
    if not _sites:
        site = Site.objects.create(domain=_hostname, name=_hostname)
    else:
        site = _sites[0]
        site.domain = _hostname
        site.name = _hostname
    site.save()
except:
    pass
