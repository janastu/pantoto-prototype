from django.http import HttpResponseRedirect,Http404
from django.contrib import messages
from pantoto import Pantoto

def get_object_or_404(klass,*args,**kwargs):
    """
        Uses objects.get() to return an object, or raises a Http404 exception if the object
        does not exist.
    """
    try:
        field = kwargs.keys()[0]
        val = kwargs.values()[0]
        return klass.objects.get()
    except klass.DoesNotExist:
        raise Http404('No %s matches the given query.' % model.__class__.name__)


def message_and_redirect(request,message,redirect_to,success=True):
    if success:
        messages.success(request,message)
    else:
        messages.error(request,message)
    return HttpResponseRedirect(redirect_to)
    
