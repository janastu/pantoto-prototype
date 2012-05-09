from django.conf.urls.defaults import *

urlpatterns = patterns('cms.views.admin',

    # Example:
    # (r'^pantoto_lite/', include('pantoto_lite.foo.urls')),

    (r'^$','do_show_dashboard'),

    (r'view/new/$','do_add_view'),

    (r'view/(?P<view_id>\w+)/edit/$','do_edit_view'),

    (r'view/(?P<view_id>\w+)/get_fal/$', 'get_view_fal'),

    (r'view/(?P<view_id>\w+)/pagelets/$', 'do_view_pagelets'),

    (r'pagelet/(?P<page_id>\w+)/properties/$', 'do_pagelet_properties'),

    (r'pagelet/(?P<pagelet_id>\w+)/order_fields/$','do_pagelet_order_fields'),

    (r'pagelet/(?P<pagelet_id>\w+)/edit/$','do_edit_pagelet'),

    (r'category/(?P<category_id>\w+)/order/$','do_category_order_children'),

    (r'file/new/$','do_add_file'),

    (r'file/(?P<file_id>\w+)/delete/$','do_delete_file'),

    (r'conf/change_site/$','do_change_site'),

)


urlpatterns += patterns('cms.views.generic',

    (r'(?P<model>\w+)/list/$','objects_list'),

    (r'(?P<model>\w+)/new/$','add_object'),

    (r'(?P<model>\w+)/(?P<obj_id>\w+)/edit/$','edit_object'),

    (r'(?P<model>\w+)/(?P<obj_id>\w+)/delete/$','delete_object'),

)

