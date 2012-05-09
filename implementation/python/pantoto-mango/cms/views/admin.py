from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.contrib import messages
from django.http import HttpResponse,Http404,HttpResponseRedirect
from cms.auth.decorators import login_required
from pantoto.models import * 
from pantoto.shortcuts import get_object_or_404
from pantoto.helpers import to_form_data,handle_uploaded_file,delete_file
from pantoto import Pantoto
from cms.views.generic import do_post_pagelet
from pantoto.forms import FileForm,EditFileForm

@login_required
def do_show_dashboard(request):
    return render_to_response('admin/index.html',{'title':'Dashboard'},context_instance = RequestContext(request))

@login_required
def do_change_site(request):
    if request.method == "POST":
        site = Site.objects.get(id=request.POST['site'])
        site_theme = Theme.objects.get(id=request.POST['site_theme'])
        admin_theme = Theme.objects.get(id=request.POST['admin_theme'])
        users = []
        if request.POST.getlist('personas'):
            for persona_id in request.POST.getlist('personas'):
                persona = Persona.objects.get(id=persona_id)
                for user in persona.users:
                    if user not in users:
                        users.append(user)
        else:
            users.append(request.user)
            request.session['site'] = site
        print users
        for user in users:
            user_setting = UserSetting.objects.get_or_create(user=user)[0]
            user_setting.site = site
            user_setting.site_theme = site_theme
            user_setting.admin_theme = admin_theme
            user_setting.save()
        messages.success(request,'Successfully changed site & themes')
        return HttpResponseRedirect('/admin/')
    else:
        return render_to_response('admin/change_site.html',{'title':'Change Site & Themes','sites':Site.get_for_choices(blank_choice=False),\
            'personas':Persona.get_for_choices(),'site_themes':Theme.get_for_choices(theme_type='site'),\
            'admin_themes':Theme.get_for_choices()},context_instance = RequestContext(request))

@login_required
def do_add_view(request):
    PERMISSIONS = (
           ("rw","Read-Write"),
           ("r-","Read-Only"),
           ("-w","Write-Only"),
           ("rn","Read-Restricted"),
           ("nw","Write-Restricted")
    )
    if request.method == "POST":
        fal = simplejson.loads(request.POST.get('fal','{}'))
        view = View(name=request.POST['name'],description=request.POST.get('description',''))
        view.fal = fal
        fields = []
        for fid in request.POST.getlist('fields[]'):
            fields.append(Field.objects.get(id=fid))
        view.fields = fields
        view.save()
        messages.success(request,'Successfully added View "%s"' % view.name)
        return HttpResponse(simplejson.dumps({'success':True}),mimetype="application/javascript")
    else:
        return render_to_response('admin/add_edit_view.html',{'add':True,'title':'Add New View','fields':Field.get_for_choices(),\
            'personas':Persona.get_for_choices(),'permissions':PERMISSIONS},context_instance=RequestContext(request))

@login_required
def do_edit_view(request,view_id):
    PERMISSIONS = (
           ("rw","Read-Write"),
           ("r-","Read-Only"),
           ("-w","Write-Only"),
           ("rn","Read-Restricted"),
           ("nw","Write-Restricted")
    )
    view = View.objects.get(id=view_id)
    if request.method == "POST":
        fal = simplejson.loads(request.POST.get('fal','{}'))
        view.name = request.POST['name']
        view.description = request.POST.get('description','')
        fields = []
        for fid in request.POST.getlist('fields[]'):
            fields.append(Field.objects.get(id=fid))
        view.fields = fields
        view.fal = fal
        view.save()
        messages.success(request,'Successfully updated View ' + view.name)
        return HttpResponse(simplejson.dumps({'success':True}),mimetype="application/javascript")
    else:
        return render_to_response('admin/add_edit_view.html',{'add':False,'name':view.name,'description':view.description,\
                'title':'Edit View','fields':view.sel_fields(),'vid':view_id,\
                'permissions':PERMISSIONS,'personas':Persona.get_for_choices()},context_instance=RequestContext(request))

@login_required
def get_view_fal(request,view_id):
    view = View.objects.get(id=view_id)
    fal = view.fal
    field_map = {}
    persona_map = {}
    for fid,perms in fal.items():
        field_map[fid] = Field.objects.get(id=fid).label
        for pid in perms.keys():
            if not persona_map.has_key(pid):
                persona_map[pid] = Persona.objects.get(id=pid).name
    return HttpResponse(simplejson.dumps({'fal':fal,'field_map':field_map,'persona_map':persona_map}),mimetype="application/javascript")

@login_required
def do_pagelet_properties(request,page_id):
    pagelet = Pagelet.objects.get(id=page_id)
    if request.method == "POST":
        pantoto = Pantoto()
        context = pantoto.get_add_edit_object_form("pagelet-property",data=request.POST)
        form = context['form']
        if form.is_valid():
            obj = pantoto.save_object_from_form('pagelet-property',form.cleaned_data,request=request)
            obj.field_order = pagelet.opts.field_order
            pagelet.opts = obj
            pagelet.save()
            messages.success(request,'Successfully updated properties of pagelet "%s"' % pagelet.title)
            return HttpResponseRedirect('/admin/pagelet/list/')
    else:
        context = Pantoto().get_add_edit_object_form("pagelet-property",initial=to_form_data(pagelet.opts))
        context['title'] = pagelet.title+" Properties"
        context['model'] = 'pagelet'
        return render_to_response('admin/add_edit.html',context,context_instance=RequestContext(request))

@login_required
def do_pagelet_order_fields(request,pagelet_id):
    pagelet = Pagelet.objects.get(id=pagelet_id)
    if request.is_ajax():
        pagelet.opts.field_order = simplejson.loads(request.POST['order'])
        pagelet.save()
        messages.success(request,'Successfully updated fields order for "' + pagelet.title + '"' )
        return HttpResponse(simplejson.dumps({'redirect':'/admin/pagelet/list/'}),mimetype="application/javascript")
    else:
        fields = [ (field.id,field.label) for field in Pantoto().get_pagelet_fields(pagelet,request.user) ]
        return render_to_response('admin/order_fields.html',{'fields':fields},context_instance=RequestContext(request))

@login_required
def do_category_order_children(request,category_id):
    category = Category.objects.get(id=category_id)
    if request.is_ajax():
        category.children_order = simplejson.loads(request.POST['order'])
        category.save()
        messages.success(request,'Successfully updated children order for category"' + category.name + '"' )
        return HttpResponse(simplejson.dumps({'redirect':'/admin/category/list/'}),mimetype="application/javascript")
    else:
        fields = [ (cat.id,cat.name) for cat in category.get_children() ]
        return render_to_response('admin/order_fields.html',{'fields':fields},context_instance=RequestContext(request))

@login_required
def do_edit_pagelet(request,pagelet_id):
    return do_post_pagelet(request,pagelet_id=pagelet_id)
    
@login_required
def do_view_pagelets(request,view_id):
    view = View.objects.get(id=view_id)
    headers,pagelets = Pantoto().get_view_pagelets(view,request.user)
    return render_to_response('admin/view_pagelets.html',{'title':'View '+view.name+' Pagelets','model':'view',\
                                                           'pagelets':pagelets,'headers':headers},context_instance=RequestContext(request))
 
@login_required
def do_add_file(request):
    if request.method == "POST":
        form = FileForm(request.POST,request.FILES)
        if form.is_valid():
            name,extension,path,url,size = handle_uploaded_file(request.FILES['_file'])
            new_file = File(name=name,extension=extension,description=form.cleaned_data['description'],path=path,url=url,size=size)
            new_file.save()
            messages.success(request,'Successfully uploaded File ' + name)
            return HttpResponseRedirect('/admin/file/list/')
    else:
        pass
    return render_to_response('admin/add_edit.html',{'add':True,'title':'Add New File','form':FileForm(),'upload':True},context_instance=RequestContext(request))

@login_required
def do_delete_file(request,file_id):
    _file = File.objects.get(id=file_id)
    if not _file:
        raise Http404('File Does Not Exist')
    if request.method == "POST":
        delete_file(_file.path)
        messages.success(request,'Successfully deleted File ' + _file.name)
        _file.delete()
        return HttpResponseRedirect('/admin/file/list/')
    else:
        return render_to_response('admin/delete.html',{'module':'File','obj':_file},context_instance=RequestContext(request))

