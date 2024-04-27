"""
Functions for django-distill to generate URL kwargs for distill_path. Models are
imported within functions to avoid circular imports. Note that the HomePage and
Site Feed require no kwargs, so they are not included here.
"""
from django.apps import apps
from django.conf import settings
from django.core.paginator import Paginator


def home_paginated():
    """Return an iterable url kwarg dicts for the home_paginated view."""
    from genericsite.models import Article

    g = apps.get_app_config("genericsite")
    articles = Article.objects.live().filter(site_id=settings.SITE_ID)
    paginator = Paginator(articles, g.paginate_by, orphans=g.paginate_orphans)
    return ({"page": page} for page in paginator.page_range)


def sections():
    """Return an iterable url kwarg dicts for the section_page view."""
    from genericsite.models import Section

    return (
        {"section_slug": section.slug}
        for section in Section.objects.live().filter(site_id=settings.SITE_ID)
    )


def sections_paginated():
    """Return an iterable url kwarg dicts for the section_paginated view."""
    from genericsite.models import Section

    g = apps.get_app_config("genericsite")

    sections = Section.objects.live().filter(site_id=settings.SITE_ID)
    paginator = Paginator(sections, g.paginate_by, orphans=g.paginate_orphans)

    return (
        {"section_slug": section.slug, "page": page}
        for section in sections
        for page in paginator.page_range
    )


def section_feeds():
    """Return an iterable url kwarg dicts for the section_feed view."""
    from genericsite.models import Section

    return (
        {"section_slug": section.slug}
        for section in Section.objects.live().filter(site_id=settings.SITE_ID)
    )


def landing_pages():
    """Return an iterable url kwarg dicts for the landing_page view."""
    from genericsite.models import Page

    return (
        {"page_slug": page.slug}
        for page in Page.objects.live().filter(site_id=settings.SITE_ID)
    )


def article_pages():
    """Return an iterable url kwarg dicts for the article_page view."""
    from genericsite.models import Article

    return (
        {"section_slug": article.section.slug, "article_slug": article.slug}
        for article in Article.objects.live().filter(site_id=settings.SITE_ID)
    )
