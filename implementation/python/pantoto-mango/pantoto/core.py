from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.template import loader,Context
from django import forms
from pantoto.models import *
from pantoto.exceptions import *
from pantoto.admin import *
from pantoto.utils import headerify,to_classname
from pantoto.forms import *
from pantoto.helpers import update_obj_from_dict
import datetime

__all__ = ('Pantoto',)

class Pantoto(object):
    """
        Singleton Pantoto core class
    """

    #Global Declarations
    _instance = None
    FORMATS = ('list','json')

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Pantoto, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __get_class__(self,model):
        """
            Returns class for given model name
        """
        model = to_classname(model)
        if model not in self.__get_models__():
            raise InvalidModel("Model %s is not invalid" % model)
        return eval(model)

    def __get_admin_class__(self,model):
        """
            Returns admin class for given model name
        """
        model = to_classname(model)
        if model not in self.__get_models__():
            raise InvalidModule("The requested module is invalid")
        return eval(model+"Admin")
             
    def __reset_db__(self):
        """
            Reset database
        """
        models_to_reset = ('User','Persona','Field','View','Category','Pagelet','Site','File','Theme','UserSetting','IdCounter')
        for model in models_to_reset:
            klass = eval(model)
            klass.objects.delete()

    def __get_models__(self):
        """
            Returns all models
        """
        return MODELS
    
    def __make_form__(self,fields,name='DynaForm'):
        """
            Builds Django form dynamically
        """
        return type(name, (forms.BaseForm,), { 'base_fields': fields })

    def __make_form_field__(self,name,field_type,label,required,max_length=255,initial="",choices=None,help_text='',rows=24,cols=80,readonly=False):
        #@TODO:Readonly for all fields .. presently done only for text field
        if (field_type == "StringField" and choices) or field_type == "ReferenceField":
            return {name:forms.ChoiceField(label=label,required=required,help_text=help_text,initial=initial,choices=choices)}
        if field_type == "StringField":
            if readonly:
                return {name:forms.CharField(label=label,max_length=max_length,help_text=help_text,required=required,initial=initial,\
                                        widget=forms.TextInput(attrs={'readonly':'readonly'}))}
            else:
                return {name:forms.CharField(label=label,max_length=max_length,help_text=help_text,required=required,initial=initial)}
        if field_type == "SlugField":
                return {name:forms.SlugField(label=label,max_length=max_length,help_text=help_text,required=required,initial=initial)}
        if field_type == "PasswordField":
            return {name:forms.CharField(label=label,max_length=max_length,help_text=help_text,required=required,initial=initial,\
                               widget=forms.PasswordInput(render_value=False))}
        if field_type == "TextField":
            return {name:forms.CharField(label=label,help_text=help_text,required=required,initial=initial,\
                               widget=forms.Textarea(attrs={'rows':rows,'cols':cols}))}
        if field_type == "EmailField":
            return {name:forms.EmailField(label=label,help_text=help_text,required=required,initial=initial)}
        if field_type == "BooleanField":
            return {name:forms.BooleanField(label=label,help_text=help_text,required=required,initial=initial)}
        if field_type == "IntField":
            if readonly:
                return {name:forms.IntegerField(label=label,help_text=help_text,required=required,initial=initial,\
                                                                widget=forms.TextInput(attrs={'readonly':'readonly'}))}
            else:
                return {name:forms.IntegerField(label=label,help_text=help_text,required=required,initial=initial)}
        if field_type == "FloatField":
            return {name:forms.FloatField(label=label,help_text=help_text,required=required,initial=initial)}
        if field_type == "ListField":
            return {name:forms.MultipleChoiceField(label=label,required=required,help_text=help_text,initial=initial,choices=choices)}
        return {}

    def __get_admin_includes__(self,model):
        """
            Returns admin page includes ( css,js files )
        """
        admin_klass = self.__get_admin_class__(model)
        includes = [] 
        if not hasattr(admin_klass,"Media"):
            return "" 
        if hasattr(admin_klass.Media,"css"):
            for css_file in admin_klass.Media.css:
                includes.append('<link rel="stylesheet" type="text/css" href="%s" />' % css_file)
        if hasattr(admin_klass.Media,"js"):
            for js_file in admin_klass.Media.js:
                includes.append('<script type="text/javascript" src="%s"></script>' % js_file)
        buttons = []
        if hasattr(admin_klass,'custom_buttons'):
            for button in admin_klass.custom_buttons:
                buttons.append("<input type='button' value='%s' onclick='javascript:add_hidden_field(\"%s\",\"%s\");' />" % \
                                (button['label'],button['dest'],button['set_val']))
        if hasattr(admin_klass,'redirect_button'):
            button = admin_klass.redirect_button[0]
            buttons.append("<input type='button' value='%s' onclick='javascript:add_hidden_field(\"%s\",\"%s\");' />" % \
                                (button.keys()[0],'redirect',button.values()[0]))
        return {'includes':"\n".join(includes),'buttons':buttons}

    def __get_list_headers__(self,model):
        """
            Returns Headers for object list table
        """
        klass = self.__get_class__(model)
        list_display = self.__get_admin_class__(model).list_display['cols']
        headers = []
        for obj in klass.objects(): 
            for col in list_display:
                if hasattr(obj,col):
                    func = getattr(obj,col)
                    if callable(func) and hasattr(func,"short_description"):
                        headers.append(getattr(func,"short_description"))
                    else:
                        headers.append(headerify(col))
            break
        return headers

    def __get_form_spec__(self,model,edit=False):
        if edit:
            spec_name = 'Edit%sForm' % to_classname(model)
            try:
                return eval(spec_name)
            except NameError:
                pass
        spec_name = '%sForm' % to_classname(model)
        try:
            return eval(spec_name)
        except NameError:
            return eval("BaseForm")

    def __build_form__(self,model,obj_id=None,obj_name=None,edit=False):
        klass = self.__get_class__(model)
        spec = self.__get_form_spec__(model,edit)()
        #Build form based on model fields
        fields = SortedDict({})
        if hasattr(spec,'extra_fields'):
            for name,field in spec.extra_fields.items():
                fields.update({name:field})
        for field in klass._fields.values():
            if not field.editable:
                continue
            if hasattr(spec,'exclude_fields'):
                if field.name in spec.exclude_fields:
                    continue
            if not field.label:
                label = headerify(field.name)
            else:
                label = field.name
            if field.required:
                label += ' *'
            if field.type == 'ListField' and field.field.type == 'ReferenceField':
                choices = field.field.document_type_obj.get_for_choices()    
            elif field.type == 'ReferenceField':
                if field.document_type_obj == "self":
                    choices = field.document_type.get_for_choices()
                    # Remove self reference from choices
                    if obj_id:
                        try:
                            choices.remove((obj_id,obj_name))
                        except ValueError:
                            pass
                else:
                    if model == "site" and field.document_type_obj.__name__ == "Category":
                        choices = [ (cat.id,cat.name) for cat in Category.objects(type="sitehome") ] 
                        choices.insert(0,("","=== Select =="))
                    else:
                        choices = field.document_type_obj.get_for_choices()
            elif field.choices:
                choices = field.choices
            else:
                choices = None
            if hasattr(field,'max_length') and field.max_length:
                max_length = field.max_length
            else:
                max_length = 255
            if field.default:
                default = field.default 
            else:
                default = ""
            field_dict = self.__make_form_field__(name=field.name,field_type=field.type,label=label,required=field.required,\
                                max_length=max_length,initial=default,choices=choices,help_text=field.help_text)
            if field_dict:
                fields.update(field_dict)
        return self.__make_form__(fields,'AddEditForm')

    def __get_pagelet_merged_fal__(self,pagelet):
        """
            Returns merged fal for the given pagelet
            for eg: rw r-: rw
        """
        MERGE_RULES = {
            '----':'--',
            'r--w':'-w',
            'r---':'r-',
            'r-rw':'rw',
            'rw-w':'-w',
            'rw--':'rw',
            '-w--':'-w',
            'r-r-':'r-',
            'rwrw':'rw',
            '-w-w':'-w',
        }
        mv = {}
        for view in pagelet.opts.views:
            for fid,perms in view.fal.items():
                if mv.has_key(fid):
                    for perm_id,perm in perms.items():
                        if perm_id in mv[fid].keys():
                            mvperms = mv[fid]
                            if MERGE_RULES.has_key(perm+mvperms[perm_id]):
                                mvperms[perm_id] = MERGE_RULES[perm+mvperms[perm_id]]
                            else:
                                mvperms[perm_id] = MERGE_RULES[mvperms[perm_id]+perm]
                            mv[fid] = mvperms
                        else:
                            mv[fid].update({perm_id:perm})
                else:
                    mv.update({fid:perms})
        return mv

    def __get_pagelet_field_perms__(self,pagelet,user):
        """
            Gets visible pagelet fields with permissions for the logged in user
        """
        field_perms = {}
        for fid,perms in self.__get_pagelet_merged_fal__(pagelet).items():
            for persona,perm in perms.items():
                if user.belongs_to_persona(persona):
                    if perm == '-w':
                        if pagelet.opts.prototype:
                            field_perms.update({fid:'w'})
                        else:
                            field_perms.update({fid:'r'})
                    elif perm == 'r-':
                        field_perms.update({fid:'r'})
                    elif perm == 'rw':
                        field_perms.update({fid:'w'})
                    elif perm == '--':
                        field_perms.update({fid:'w'})
        return field_perms

    def __get_pagelet_fields_order__(self,pagelet,user):
        field_order = self.get_pagelet_fields(pagelet,user,only_names=True)
        if not pagelet.opts.field_order:
            return []
        if pagelet.opts.type == "form_only":
            fields = []
        else:
            fields = ['title','description']
        return fields.extend(field_order)

    def __get_pagelet_form__(self,pagelet,user,post={}):
        """
            Generates pagelet form 
        """
        if pagelet.opts.type == "form_only":
            fields = SortedDict({})
        else:
            fields = SortedDict({'title':forms.CharField(label='Title',max_length=255,initial=pagelet.title),\
                                'description':forms.CharField(label='Description',widget=forms.Textarea(attrs={'rows':30,'cols':85}),initial=pagelet.description)})
        for fid,perm in self.__get_pagelet_field_perms__(pagelet,user).items():
            if perm == 'r':
                readonly = True
            else:
                readonly = False
            field = Field.objects.get(id=fid)
            fields.update(self.__make_form_field__(field.get_form_field_name(),field.type,field.label,field.required,field.max_length,\
                          field.get_initial(),field.get_choices(),field.help_text,field.rows,field.cols,readonly))
        PageletForm = self.__make_form__(fields,'PostPageletForm')
        if post:
            form = PageletForm(post)
        elif pagelet.post_data:
            form = PageletForm(initial=self.get_pagelet_post_data(pagelet,user))
        else:
            form = PageletForm()
        field_order = self.__get_pagelet_fields_order__(pagelet,user)
        if field_order:
            form.fields.keyOrder = field_order
        return form

    def __save_pagelet_post__(self,pagelet,user,post):
        """
            Saves post data for given pagelet
        """
        pagelet.post_data = {}
        for field in self.get_pagelet_fields(pagelet,user):
            if post.has_key(field.get_form_field_name()):
                pagelet.post_data.update({field.id:post[field.get_form_field_name()]})
        return pagelet

    def init_db(self,reset_only=False):
        """
            Initialized database with default db dump

            @TODO: Backup option 

            Warning: Use this method carefully as it destory all existing data with backup
        """
        self.__reset_db__()
        if not reset_only:
            # Create Guest User
            guest = User(username='guest',email='guest@servelots.com',password='guest')
            guest.first_name = 'Guest'
            guest.last_name = 'Servelots'
            guest.save()

            # Create Guest Persona
            guest_persona = Persona(name='guests',description='Guest Persona')
            guest_persona.users = [guest] 
            guest_persona.save()

            # Create Super User
            admin = User(username='admin',email='admin@servelots.com',password='admin')
            admin.first_name = 'Admin'
            admin.last_name = 'Servelots'
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()

            # Create Default Admin Themes
            admin_theme = Theme(name='Admin Bluez',slug='adminbluez',description='Default Admin Theme',type='admin')
            admin_theme.save()

            Theme(name='Admin Redz',slug='adminredz',description='Red Theme for Admin',type='admin').save()
            Theme(name='Admin Blackz',slug='adminblackz',description='Black Theme for Admin',type='admin').save()
            Theme(name='Admin Accessible',slug='adminaccessible',description='Accessible Theme for Admin',type='admin').save()

            # Create Default Site 
            site = Site(name='Pantoto Lite',slug='pantoto',description='...Redefining CMS')
            site.save()

            # Create Default Site Themes
            site_theme = Theme(name='Site Bluez',slug='sitebluez',description='Default Site Theme',type='site')
            site_theme.save()

            Theme(name='Site Redz',slug='siteredz',description='Red Theme for site',type='site').save()
            Theme(name='Site Greenz',slug='sitegreenz',description='Green Theme for site',type='site').save()
            Theme(name='Site Accessible',slug='siteaccessible',description='Accessible Theme for site',type='site').save()


            # Create UserSetting for admin user
            user_setting = UserSetting(user=admin,site=site,site_theme=site_theme,admin_theme=admin_theme)
            user_setting.save()
        return

    def get_view_pagelets(self,view,user):
        """
            Returns all the pagelets for the given view
        """
        headers = ["Pagelet ID","Pagelet Title"]
        headers.extend([ headerify(field.label) for field in view.fields ])
        rows = []
        for pagelet in Pagelet.objects(opts__views=view,opts__prototype=False):
            row = [pagelet.id,pagelet.title]
            for field in view.fields:
                if field in self.get_pagelet_fields(pagelet,user):
                    row.append(pagelet.post_data.get(field.id,''))
                else:
                    row.append('x')
            rows.append(row)
        return headers,rows

    def get_pagelet_post_data(self,pagelet,user):
        """
            Returns post_data for the pagelet
        """
        post_data = {}
        for field in self.get_pagelet_fields(pagelet,user):
            field_name = field.get_form_field_name()
            if pagelet.post_data.has_key(field.id):
                post_data.update({field_name:pagelet.post_data[field.id]})
        return post_data

    def check_pagelet_submit_once(self,pagelet,user):
        if pagelet.opts.submit_once:
            authored = self.is_pagelet_author(pagelet,user,recursive=True)
            belongs_to_persona = False
            for persona in pagelet.opts.submit_once_personas:
                if user.belongs_to_persona(persona.id):
                    belongs_to_persona = True
                    break
            if authored and belongs_to_persona:
                return False
        return True

    def post_pagelet(self,pagelet,user,post=None):
        if not self.check_pagelet_submit_once(pagelet,user):
            if pagelet.opts.submit_once_message:
                return (False,pagelet.opts.submit_once_message)
            else:
                return (False,"You can only submit this pagelet only once.")
        if not pagelet.opts.form_title:
            form_title = 'Post Pagelet'
        else:
            form_title = pagelet.opts.form_title
        if post:
            form = self.__get_pagelet_form__(pagelet,user,post)
            if not form.is_valid():
                return (False,{'form_title':form_title,'form':form})
            if pagelet.opts.prototype:
                title = post.get('title',pagelet.title)
                new_pagelet = Pagelet(title=title,description=post.get('description',''))
                new_pagelet.opts = PageletProperty()
                new_pagelet.opts.views = pagelet.opts.views
                new_pagelet.add_author(user)
                new_pagelet.opts.type = pagelet.opts.type
                new_pagelet.opts.field_order = pagelet.opts.field_order
                new_pagelet.opts.form_title = pagelet.opts.form_title
                if pagelet.opts.on_submit == "attach_views":
                    for view in pagelet.opts.attach_views:
                        if not view in new_pagelet.opts.views:
                            new_pagelet.opts.views.append(view)
                if pagelet.opts.auto_title:
                    context = Context({'title':pagelet.title,'user':user.username,\
                                                        'date':datetime.datetime.now().strftime(settings.DATE_FORMAT)})
                    new_pagelet.title = loader.get_template_from_string(pagelet.opts.title_template).render(context)
                new_pagelet = self.__save_pagelet_post__(new_pagelet,user,post)
                new_pagelet.save()
                pagelet.add_child(new_pagelet,save=True)
                return (True,'Successfully posted pagelet "%s"' % new_pagelet.title)
            else:
                if post.get('title',None):
                    pagelet.title = post['title']
                pagelet.description = post.get('description','')
                pagelet.add_author(user)
                pagelet = self.__save_pagelet_post__(pagelet,user,post)
                pagelet.save()
                return (True,'Successfully posted pagelet "%s"' % pagelet.title)
        else:
           form = self.__get_pagelet_form__(pagelet,user)
           return (True,{'form_title':form_title,'form':form})

    def is_pagelet_author(self,pagelet,user,recursive=False):
        if not recursive:
            return user in pagelet.authors
        for child in pagelet.get_children():
            if user in child.authors:
                return True
        return False

    def get_pagelet_fields(self,pagelet,user,only_names=False):
        fields = self.__get_pagelet_field_perms__(pagelet,user).keys()
        field_order = pagelet.opts.field_order
        # Order Fields
        ordered_fields = []
        for fid in field_order:
            if fid in fields:
                ordered_fields.append(fid)
        for fid in fields:
            if fid not in ordered_fields:
                ordered_fields.append(fid)
        if only_names:
            return [ Field.objects.get(id=fid).get_form_field_name() for fid in ordered_fields ]
        else:
            return [ Field.objects.get(id=fid) for fid in ordered_fields ]
        
    def get_add_edit_object_form(self,model,data={},initial={}):
        if initial:
            spec = self.__get_form_spec__(model,True)()
            klass = self.__get_class__(model)
            obj_id = initial.get('id',None)
            formKlass = self.__build_form__(model,obj_id=obj_id,obj_name=initial['unicode'],edit=True)
        else:
            spec = self.__get_form_spec__(model)()
            formKlass = self.__build_form__(model)
        if hasattr(spec,'clean_methods'):
            for method in spec.clean_methods:
                setattr(formKlass,method,eval(method))
        if data:
            form = formKlass(data)
        else:
            if initial:
                form = formKlass(initial=initial)
            else:
                form = formKlass()
        if hasattr(spec,'field_order'):
            form.fields.keyOrder = spec.field_order
        if initial:
            title = 'Edit '+model.capitalize()
        else:
            title = 'Add New '+model.capitalize()
        context = {'form':form,'title':title,'add':bool(initial),'model':model}
        context.update(self.__get_admin_includes__(model))
        return context

    def get_default_site(self):
        """
            Returns default site as set in settings file DEFAULT_SITE setting
        """
        try:
            site = Site.objects.get(slug=settings.DEFAULT_SITE)
            site_theme = Theme.objects.get(slug=settings.DEFAULT_SITE_THEME)
            admin_theme = Theme.objects.get(slug=settings.DEFAULT_ADMIN_THEME)
            return (site,site_theme,admin_theme)
        except:
            # @TODO: Instead of raising exception take user to site creation form. 
            raise ImproperlyConfigured('Default Site and/or Theme Does not exist. Run "initdb" management command to initiate the database')


    def set_current_site_for_user(self,request):
        try:
            user_setting = UserSetting.objects.get(user=request.user)
        except UserSetting.DoesNotExist:
            user_setting = None
        default_site,default_site_theme,default_admin_theme = self.get_default_site()
        if user_setting and user_setting.site:
            request.session['site'] = user_setting.site
        else:
            request.session['site'] = default_site
        if user_setting and user_setting.site_theme:
            request.session['site_theme'] = user_setting.site_theme
        else:
            request.session['site_theme'] = default_site_theme
        if user_setting and user_setting.admin_theme:
            request.session['admin_theme'] = user_setting.admin_theme
        else:
            request.session['admin_theme'] = default_admin_theme
        return


    def get_pagelets_for_category(self,category):
        return Pagelet.objects(opts__categories=category)

    def get_current_site(self,request):
        """
            Returns current site,site_theme,admin_theme
        """
        if not request.session.get('site',None):
            #If user is not authenticated return the site mentioned in the default_site setting in settings file 
            site = None
            try:
                user_setting = UserSetting.objects.get(user=request.user)
                if user_setting.site:
                    site,site_theme,admin_theme = (user_setting.site,user_setting.site_theme,user_setting.admin_theme)
            except UserSetting.DoesNotExist:
                pass
            if not site:
                site,site_theme,admin_theme = self.get_default_site()
            request.session['site'] = site
            request.session['site_theme'] = site_theme
            request.session['admin_theme'] = admin_theme
        return (request.session['site'],request.session['site_theme'],request.session['admin_theme'])

    def save_object_from_form(self,model,data,_id=None,request=None):
        post = request.POST
        klass = self.__get_class__(model)
        admin_klass = self.__get_admin_class__(model)
        if hasattr(admin_klass,'custom_buttons'):
            for button in admin_klass.custom_buttons:
                field = button['dest']
                if hasattr(klass,field) and post.has_key(field):
                    data.update({field:post[field]})
        if klass.__class__.__name__ == "DocumentMetaclass":
            return update_obj_from_dict(klass,data,_id)
        else:
            obj = update_obj_from_dict(klass,data,_id)
            obj.save(user=request.user)
            return obj

    def can_delete_object(self,obj):
        klass_name = obj.__class__.__name__
        if RESERVED_IDS.has_key(klass_name) and obj.id in RESERVED_IDS[klass_name]:
            return False
        return True
        
    def delete_object(self,model,obj_id):
        """
            Deletes object with given id for the specified model. If the object does'nt exist or cant delete returns False with error message.
            On success returns True with success message
        """
        obj = self.get_object(model,obj_id)
        if not obj:
            return (False,'Object Doest Not Exist')
        # Check for reserved ids before deleting
        if not self.can_delete_object(obj):
            return (False,'Can not delete reserved %s  "%s".' % (model,obj))
        obj.delete()
        return (True,'Successfully deleted %s "%s"' % (model,obj))

    def get_object(self,model,obj_id):
        """
            Returns object with given id for the specified model. If the object does'nt exist returns None
        """
        klass = self.__get_class__(model)
        try:
            return klass.objects.get(id=obj_id)
        except klass.DoesNotExist:
            return None

    def get_objects(self,model,page=1,frmt="list"):
        """
            Returns objects for the given model
        """
        if frmt not in self.FORMATS:
            raise InvalidFormat("The requested format is invalid")
        klass = self.__get_class__(model)
        admin_klass = self.__get_admin_class__(model)
        list_display = admin_klass.list_display['cols']
        rows = []
        for obj in klass.objects: 
            row = []
            for col in list_display:
                if hasattr(obj,col):
                    func = getattr(obj,col)
                    if callable(func):
                        val = func()
                    else:
                        val = func
                    # Check if value is of boolean type if yes then display icon else value
                    if type(val).__name__ == 'bool':
                        if val:
                            row.append('<img src="/static/base/images/icon_accept.png" alt="Yes" />')
                        else:
                            row.append('<img src="/static/base/images/icon_cross.png" alt="No" />')
                    else:
                        row.append(val)
            if row:
                #Append Actions
                actions = ["<a href='/admin/%s/%s/edit/' title='Edit %s'> <img src='/static/base/images/icon_edit.png' alt='Edit'\
                            class='mid_align'> </a>" % (model,obj.id,model) ]
                actions.append("<a href='/admin/%s/%s/delete/' title='Delete %s'> <img src='/static/base/images/icon_delete.png' alt='Delete'\
                            class='mid_align'> </a>" % (model,obj.id,model)) 
                if admin_klass.list_display.has_key('actions'):
                    for action in admin_klass.list_display['actions']:
                        func = getattr(obj,action)
                        if callable(func):
                            val = func()
                            if val:
                                actions.append(val)
                row.append("&nbsp;|&nbsp;".join(actions))
                if model == "category":
                    if obj.parent:
                        rows.append(((obj.id,obj.parent.id),row))
                    else:
                        rows.append(((obj.id,'None'),row))
                else:
                    rows.append(row)
        title = 'List '+klass.meta.get('verbose_name_plural',model.capitalize()+"s")
        context = {'cols':self.__get_list_headers__(model),'objs':rows,'title':title,'model':model}
        context.update(self.__get_admin_includes__(model))
        return context

   

