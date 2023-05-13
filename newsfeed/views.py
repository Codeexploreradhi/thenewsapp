# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import PieChart
from .news_db import NewsDB

import time


META_KEYWORDS = "Specious News uses k-means clustering to learn about topics from news articles " + \
                 "based on their similarities."


def show_news_topics(request):
    _topics = NewsDB().fetch_topics()
    _meta_keywords = _topics[0]['title'] if _topics else META_KEYWORDS
    return render(request, "newsfeed/news.html", {"topics": _topics, "meta_keywords": _meta_keywords})


def show_articles_by_topic(request, topic_id):
    _keywords, _articles = NewsDB().fetch_articles_by_topic(topic_id)
    _meta_keywords = _articles[0]['summary'][0:160] if _articles else META_KEYWORDS
    return render(request, "newsfeed/articles.html",
                  {"articles": _articles,
                   "keywords": _keywords, "meta_keywords": _meta_keywords})


def show_news_keywords(request):
    _topics = NewsDB().fetch_keywords()
    _meta_keywords = _topics[0]['title'] if _topics else META_KEYWORDS
    return render(request, "newsfeed/keywords.html", {"topics": _topics, "meta_keywords": _meta_keywords})


def show_articles_by_keyword(request, keyword_id):
    _keywords, _articles = NewsDB().fetch_articles_by_keyword(keyword_id)
    _meta_keywords = _articles[0]['summary'][0:160] if _articles else META_KEYWORDS
    return render(request, "newsfeed/articles.html",
                  {"articles": _articles,
                   "keywords": _keywords, "meta_keywords": _meta_keywords})

@csrf_exempt
def show_search_results(request):
    if request.method == "POST":
        _search_terms = request.POST.get('search_terms')
        _articles = NewsDB().search_articles(_search_terms)
        _meta_keywords = _articles[0]['summary'][0:160] if _articles else META_KEYWORDS
        return render(request, "newsfeed/articles.html",
                      {"articles": _articles,
                       "keywords": "Search Results for '%s'" % _search_terms,
                       "meta_keywords": _meta_keywords})


def show_counts_by_source(request):
    _counts = NewsDB().counts_by_source()
    data_source = SimpleDataSource(data=_counts)
    # Chart object
    chart = PieChart(data_source, options={"title": "Articles by Source"})
    return render(request, "newsfeed/sources.html", {"num_of_sources": len(_counts) - 1,
                                                     "chart": chart, "meta_keywords": META_KEYWORDS})


def show_cluster_graph(request):
    _cluster_info = NewsDB().fetch_cluster_html()
    html = render_to_string("newsfeed/cluster.html", {"cluster": _cluster_info})
    return HttpResponse(html)


def show_about_page(request):
    _cluster_info = NewsDB().fetch_cluster_info()
    _cluster_info['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                 time.localtime(_cluster_info['last_update']))
    return render(request, "newsfeed/about.html", {"cluster": _cluster_info, "meta_keywords": META_KEYWORDS})


def page_not_found(request):
    return render(request,
                  'newsfeed/error.html',
                  {"errorCode": 404, "errorMessage": "The page you are looking for cannot be found."})


def server_error(request):
    return render(request, 'newsfeed/error.html',
                  {"errorCode": 500,
                   "errorMessage": "The server has encountered an internal error.  Please try again a little later."})


def forbidden_resource(request):
    return render(request, 'newsfeed/error.html',
                  {"errorCode": 403,
                   "errorMessage": "Access to this resource is restricted."})


def bad_request(request):
    return render(request, 'base/error.html',
                  {"errorCode": 400,
                   "errorMessage": "The server has encountered a bad request.  Please try again a little later."})