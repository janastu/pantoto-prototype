from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse,Http404,HttpResponseRedirect
from pantoto import Pantoto
from pantoto.models import Pagelet
from pantoto.helpers import to_form_data
from pantoto.shortcuts import message_and_redirect

def get_redirect(model,post,obj):
    redirect = post.get('redirect',None)
    if redirect:
        if redirect.find('$id') != -1:
            redirect = redirect.replace('$id',obj.id)
    else:
        redirect = '/admin/%s/list/' % model
    return redirect

def objects_list(request,model,template="list.html",extra_context={}):
    context = Pantoto().get_objects(model)
    if extra_context:
        context.update(extra_context)
    return render_to_response('admin/'+template,context,context_instance=RequestContext(request))

def add_object(request,model,template="add_edit.html",extra_context={}):
    if request.method == "POST":
        pantoto = Pantoto()
        context = pantoto.get_add_edit_object_form(model,data=request.POST)
        form = context['form']
        if form.is_valid():
            obj = pantoto.save_object_from_form(model,form.cleaned_data,request=request)
            messages.success(request,'Successfully create new %s "%s"' % (model,obj))
            return HttpResponseRedirect(get_redirect(model,request.POST,obj))
    else:
        context = Pantoto().get_add_edit_object_form(model)
    if extra_context:
        context.update(extra_context)
    return render_to_response('admin/'+template,context,context_instance=RequestContext(request))

def edit_object(request,model,obj_id,template="add_edit.html",extra_context={}):
    pantoto = Pantoto()
    obj = pantoto.get_object(model,obj_id)
    initial = to_form_data(obj)
    if request.method == "POST":
        context = pantoto.get_add_edit_object_form(model,data=request.POST,initial=initial)
        form = context['form']
        if form.is_valid():
            obj = pantoto.save_object_from_form(model,form.cleaned_data,obj_id,request=request)
            messages.success(request,'Successfully updated %s "%s"' % (model,obj))
            return HttpResponseRedirect(get_redirect(model,request.POST,obj))
    else:
        context = Pantoto().get_add_edit_object_form(model,initial=initial)
    if extra_context:
        context.update(extra_context)
    return render_to_response('admin/'+template,context,context_instance=RequestContext(request))

def delete_object(request,model,obj_id):
    pantoto = Pantoto()
    obj = pantoto.get_object(model,obj_id)
    if request.method == "POST":
        name = obj
        deleted,mesg = Pantoto().delete_object(model,obj_id)
        if deleted:
            messages.success(request,mesg)
        else:
            messages.error(request,mesg)
        return HttpResponseRedirect('/admin/%s/list/' % model)
    else:
        title = 'Delete %s' % model.capitalize()
        return render_to_response('admin/delete.html',{'obj':obj,'model':model,'title':title},context_instance=RequestContext(request))

def do_post_pagelet(request,template="admin/post_pagelet.html",redirect_to='/admin/pagelet/list/',pagelet_slug=None,pagelet_id=None):
    if pagelet_id:
        pagelet = Pagelet.objects.get(id=pagelet_id)
    elif pagelet_slug:
        pagelet = Pagelet.objects.get(slug=pagelet_slug)
    else:
        raise Http404('Pagelet Does Not Exist')
    pantoto = Pantoto()
    if request.method == "POST":
        flag,context = pantoto.post_pagelet(pagelet,request.user,request.POST)
        if flag:
            return message_and_redirect(request,context,redirect_to)
    else:
        flag,context = pantoto.post_pagelet(pagelet,request.user)
        if not flag:
            return message_and_redirect(request,context,redirect_to,success=False)
    return render_to_response(template,context,context_instance=RequestContext(request)) 
