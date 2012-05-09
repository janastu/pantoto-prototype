from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',

    # Example:
    # (r'^pantoto_lite/', include('pantoto_lite.foo.urls')),

    #comment out for production
    (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),

    (r'^auth/', include('cms.conf.auth_urls')),

    (r'^admin/', include('cms.conf.admin_urls')),

)

urlpatterns += patterns('cms.views.site',

    ('^$','do_site_home'),

    ('^site/(?P<site_slug>[-\w]+)/$','do_set_site'),

    ('^pagelet/(?P<pagelet_slug>[-\w]+)/$','do_display_pagelet'),

    ('^c/(?P<category_slug>[-\w]+)/$','do_display_category'),

	('^accessibility/$', 'do_display_accessibility'),

	('^accessibility/url/$', 'do_get_source'),

)

