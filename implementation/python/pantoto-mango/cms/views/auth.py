from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect,HttpResponse,Http404
from django.contrib import messages
from cms.auth.decorators import login_required
from pantoto import Pantoto
from pantoto.models import User
from pantoto.forms import ChangePasswordForm

def do_login(request):
    if request.method == "POST":
        _next = request.POST['next']
        user = authenticate(username=request.POST['username'],password=request.POST['password'])
        if not user:
            errors = 'Invalid Username or Password'
        elif request.path.startswith('/admin/') and not user.is_staff:
            errors = 'Sorry you dont have access to admin site'
        elif not user.is_active:
            errors = 'Sorry your account is inactive.'
        else:
            login(request,user)
            #Set site and theme for current user
            Pantoto().set_current_site_for_user(request)
            return HttpResponseRedirect(_next)
    else:
        errors = ""
        _next = request.GET.get('next','/admin/')
    return render_to_response('auth/login.html',{'next':_next,'errors':errors},context_instance = RequestContext(request))

def do_logout(request):
    logout(request)
    return HttpResponseRedirect('/auth/login/?next='+request.GET.get('next','/admin/'))

def do_change_password(request,user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        form = ChangePasswordForm(user,request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request,'Successfully updated password')
            return HttpResponseRedirect('/admin/')
    else:
        form = ChangePasswordForm(user)
    return render_to_response('admin/add_edit.html',{'title':'Change Password','form':form},context_instance = RequestContext(request))

