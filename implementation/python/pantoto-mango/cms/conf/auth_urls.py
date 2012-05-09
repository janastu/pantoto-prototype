from django.conf.urls.defaults import *

urlpatterns = patterns('cms.views.auth',

    (r'^login/$', 'do_login'),

    (r'^logout/$', 'do_logout'),

    (r'^user/(?P<user_id>\w+)/change_password/$', 'do_change_password'),

)
