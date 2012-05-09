from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404,HttpResponseRedirect
from cms.auth.decorators import login_required
from cms.views.generic import do_post_pagelet
from pantoto import Pantoto
from pantoto.models import Site,Category
import os

@login_required
def do_site_home(request):
    site = request.session['site']
    if site.has_home_category():
        return do_display_category(request,site.get_home_category().slug)
    else:
        return render_to_response('site/index.html',{},context_instance = RequestContext(request))

@login_required
def do_display_category(request,category_slug):
    category = Category.objects.get(slug=category_slug)
    if not category:
        raise Http404('Category Not Found')
    if category.is_pagelets_list():
        return render_to_response('site/display_category.html',{'pagelets':Pantoto().get_pagelets_for_category(category)},\
                                                                            context_instance = RequestContext(request))
@login_required
def do_display_pagelet(request,pagelet_slug):
    return do_post_pagelet(request,template='site/display_pagelet.html',redirect_to='/',pagelet_slug=pagelet_slug)

@login_required
def do_display_accessibility(request):
    return render_to_response('site/accessibility.html',{},context_instance = RequestContext(request))

@login_required
def do_get_source(request):
    source = request.GET["url_client"]
    os.system("wget " + source)
    return render_to_response('site/get_url.html',{},context_instance = RequestContext(request))

@login_required
def do_set_site(request,site_slug):
    site = Site.objects.get(slug=site_slug)
    if not site:
        raise Http404('Site Not Found')
    request.session['site'] = site
    return HttpResponseRedirect('/')

