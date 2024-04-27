"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django_distill import distill_path
from genericsite import views as generic

from storyville import distill

# These are the urls needed for static site generation
urlpatterns = [
    # Public urls
    distill_path(
        "feed/", generic.SiteFeed(), name="site_feed", distill_file="index.rss"
    ),
    distill_path(
        "page_<int:page>.html",
        generic.HomePageView.as_view(),
        name="home_paginated",
        distill_func=distill.home_paginated,
    ),
    distill_path(
        "<slug:section_slug>/page_<int:page>.html",
        generic.SectionView.as_view(),
        name="section_paginated",
        distill_func=distill.sections_paginated,
    ),
    distill_path(
        "<slug:section_slug>/<slug:article_slug>.html",
        generic.ArticleDetailView.as_view(),
        name="article_page",
        distill_func=distill.article_pages,
    ),
    distill_path(
        "<slug:page_slug>.html",
        generic.PageDetailView.as_view(),
        name="landing_page",
        distill_func=distill.landing_pages,
    ),
    distill_path(
        "<slug:section_slug>/",
        generic.SectionView.as_view(),
        name="section_page",
        distill_func=distill.sections,
    ),
    distill_path(
        "<slug:section_slug>/feed/",
        generic.SectionFeed(),
        name="section_feed",
        distill_func=distill.section_feeds,
        distill_file="{section_slug}/index.rss",
    ),
    distill_path(
        "", generic.HomePageView.as_view(), name="home_page", distill_file="index.html"
    ),
]

# If running in admmin mode, we add these urls
if "django.contrib.admin" in settings.INSTALLED_APPS:
    admin_urlpatterns = [
        # Administrative urls, not needed for public site
        path(
            "accounts/profile/", generic.ProfileView.as_view(), name="account_profile"
        ),
        path("accounts/", include("django.contrib.auth.urls")),
        path("admin/doc/", include("django.contrib.admindocs.urls")),
        path("admin/", admin.site.urls),
        path("tinymce/", include("tinymce.urls")),
        path(
            "images/recent.json",
            generic.TinyMCEImageListView.as_view(),
            name="tinymce_image_list",
        ),
    ]
    urlpatterns = admin_urlpatterns + urlpatterns

if settings.DEBUG:
    # NOTE: When DEBUG and staticfiles is installed, Django automatically adds static
    # urls, but does not automatically serve MEDIA
    from django.conf.urls.static import static

    # Serve static and media files from development server
    # urlpatterns += staticfiles_urlpatterns()  # automatic when DEBUG on
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        # Catch-all patterns may block these if appended, hence insert
        urlpatterns.insert(0, path("__debug__/", include(debug_toolbar.urls)))
