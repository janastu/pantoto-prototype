from mongoengine import *
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict
from django.conf import settings
from django.contrib.auth.models import UNUSABLE_PASSWORD, get_hexdigest, check_password
from django import forms
from pantoto.utils import underscorify
import os
import datetime

#Global Declartions
MODELS  = ('User','Persona','Field','View','Category','Pagelet','PageletProperty','Site','File','Theme','UserSetting','IdCounter') 

RESERVED_IDS = {'User':('usr1','usr2'),'Site':('site1',),'Theme':('theme1','theme2'),'UserSetting':('setting1',)}

__all__ = MODELS + ('MODELS','RESERVED_IDS',)

class IdCounter(Document):
    klass = StringField(max_length=20,required=True,unique=True)
    counter = IntField(required=True,default=0)

class PantotoBase(Document):
    """
        Pantoto Base class that is Inherited by all core Pantoto module classes
    """
    id = StringField(max_length=10,required=True,primary_key=True,editable=False)
    created_at = DateTimeField(editable=False)
    created_by = ReferenceField("User",editable=False) 
    updated_at = DateTimeField(editable=False)
    updated_by = ReferenceField("User",editable=False)

    meta = {
        'collection': 'pantoto',
    }

    def __get_next_id__(self):
        id_counter = IdCounter.objects.get_or_create(klass=self.__class__.__name__,defaults={'counter':0})[0]
        id_counter.counter += 1
        id_counter.save()
        return str(id_counter.counter)

    def save(self,user=None,safe=True, force_insert=False):
        if not user or user.is_anonymous():
            user = User.get_guest()
        if not self.id:
            self.id = "%s%s" % (self.meta['id_prefix'],self.__get_next_id__())
            self.created_at  = datetime.datetime.now()
            if user:
                self.created_by = user
        if self.meta.has_key('slug_fields'):
            for (slug,field) in self.meta['slug_fields']:
                if not getattr(self,slug):
                    setattr(self,slug,self.id+"-"+slugify(getattr(self,field)))
        self.updated_at = datetime.datetime.now()
        if user:
            self.updated_by = user
        super(PantotoBase,self).save(safe,force_insert)

    def delete(self,safe=False):
        klass_name = self.__class__.__name__
        if RESERVED_IDS.has_key(klass_name) and self.id in RESERVED_IDS[klass_name]:
            return False
        super(PantotoBase,self).delete(safe)

    @classmethod
    def get_for_choices(cls,blank_choice=True):
        """
            Returns tuple (id,object name) for choice field choices
        """
        choices = [ (obj.id,unicode(obj)) for obj in cls.objects ]
        if blank_choice:
            choices.insert(0,('','---- Select ---'))
        return choices

class User(PantotoBase):
    """
        Users within the Pantoto authentication system are represented by this model.
    """
    username = StringField(max_length=30, required=True,unique=True)
    first_name = StringField(max_length=30)
    last_name = StringField(max_length=30)
    email = EmailField()
    password = PasswordField(max_length=128)
    is_staff = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)
    last_login = DateTimeField(default=datetime.datetime.now,editable=False)
    date_joined = DateTimeField(default=datetime.datetime.now,editable=False)

    meta = {
        'collection': 'users',
        'id_prefix': 'usr'
    }

    def __unicode__(self):
        return self.get_full_name()

    def save(self,user=None,safe=True, force_insert=False,set_password=True):
        if set_password and not self.id:
            self.set_password(self.password,save=False)
        super(User,self).save(user,safe,force_insert)

    def get_full_name(self):
        """Returns the users first and last names, separated by a space.
        """
        full_name = u'%s %s' % (self.first_name or '', self.last_name or '')
        return full_name.strip()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def set_password(self, raw_password,save=True):
        """Sets the user's password - always use this rather than directly
        assigning to :attr:`~mongoengine.django.auth.User.password` as the
        password is hashed before storage.
        """
        from random import random
        from django.contrib.auth.models import get_hexdigest
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random()), str(random()))[:5]
        hash = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hash)
        if save:
            self.save()
        return self

    def check_password(self, raw_password):
        """Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        algo, salt, hash = self.password.split('$')
        return hash == get_hexdigest(algo, salt, raw_password)

    def get_and_delete_messages(self):
        return []

    def get_personas(self):
        return [ persona.id for persona in Persona.objects(users=self.id) ]

    def belongs_to_persona(self,persona):
        return bool(persona in self.get_personas())

    @classmethod
    def create_user(cls, username, password, email=None):
        """Create (and save) a new user with the given username, password and
        email address.
        """
        now = datetime.datetime.now()
        
        # Normalize the address by lowercasing the domain part of the email
        # address.
        # Not sure why we'r allowing null email when its not allowed in django
        if email is not None:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                pass
            else:
                email = '@'.join([email_name, domain_part.lower()])
            
        user = cls(username=username, email=email, date_joined=now)
        user.set_password(password,save=False)
        user.save() 
        return user
    
    @classmethod
    def get_guest(cls):
        """
            Returns Guest User. If not found returns None
        """
        try:
            return cls.objects.get(id='usr1')
        except User.DoesNotExist:
            return None

class Persona(PantotoBase):
    """
        Personas are a generic way of categorizing users to apply permissions, or some other label, to those users. 
        A user can belong to any number of Personas.
    """
    name = StringField(max_length=30,required=True)
    description = StringField(max_length=255)
    users = ListField(ReferenceField(User))

    meta = {
        'collection': 'personas',
        'id_prefix' : 'pers'
    }

    def __unicode__(self):
        return self.name

class Field(PantotoBase):
    """
        Field  class
    """
    FIELD_TYPES = (
        ('StringField','Text'),
        ('TextField', 'Paragraph'),
        ('ReferenceField','Drop Down'),
        ('ListField','Drop Down Multiple'),
        ('CheckboxField','Check Box'),
        ('RadioField','Radio'),
        ('DateTimeField','Date Field'),
        ('DateTimeField','Date Time'),
        ('EmailField','Email'),
        ('IntField','Integer'),
        ('FloatField','Float'),
        ('URLField','URL'),
        ('FileField','File')
    )
 
    label = StringField(max_length=255,required=True)
    type = StringField(max_length = 20,choices = FIELD_TYPES)
    required = BooleanField(default=True)
    help_text = StringField(max_length=255)
    initial = StringField(max_length=255,help_text=_("Multiple Values seperated by '|' For Checkbox and Multiple Select"))
    choices = TextField(max_length=255,help_text=_("Enter choices seperated by '|'.Eg: Apple | Orange | Strawberries"))
    max_length = IntField(default=255)
    rows = IntField(default=25)
    cols = IntField(default=80)

    meta = {
        'collection': 'fields',
        'id_prefix': 'field'
    }

    def __unicode__(self):
        return self.label

    def get_type(self):
        for type in self.FIELD_TYPES:
            if type[0] == self.type:
                return type[1]

    get_type.short_description = "Type"

    def is_choice_type(self):
        return (self.type == "ListField" or self.type == "CheckboxField" or self.type == "RadioField" or self.type == "ReferenceField" )

    def get_choices(self):
        if self.is_choice_type():
            return [ (choice,choice) for choice in self.choices.strip().split('|') ]
        else:
            return None

    def get_initial(self):
        if not self.is_choice_type():
            return self.initial
        else:
            return [ (choice,choice) for choice in self.initial.strip().split('|') ]

    def get_form_field_name(self):
        return "%s_%s" % (self.id,underscorify(self.label))
            

class FieldPerm(EmbeddedDocument):
    """
        Holds Persona Permissions
    """
    field = ReferenceField(Field,required=True)
    perm = StringField(max_length=3,required=True)

class PersonaPerm(EmbeddedDocument):
    """
        Holds Persona Permissions
    """
    persona = ReferenceField(Persona,required=True)
    field_perms = ListField(EmbeddedDocumentField(FieldPerm),required=True) 

class View(PantotoBase):
    """
        View Class
    """
    name = StringField(max_length=30,required=True)
    description = StringField(max_length=255)
    fields = ListField(ReferenceField(Field))
    fal = DictField(editable=False) 

    meta = {
        'collection': 'views',
        'id_prefix' : 'view'
    }

    def __unicode__(self):
        return self.name

    def delete(self,safe=False):
        # Remove all pagelet references
        for pagelet in Pagelet.objects(opts__views=self):
            del pagelet.opts.views[pagelet.opts.views.index(self)]
        super(PantotoBase,self).delete(safe)
    
    def get_pagelets_link(self):
        return '<a href="/admin/view/%s/pagelets/" title="Show Pagelets for this view"> Pagelets <a>' % self.id

    get_pagelets_link.short_description = 'Pagelets' 

    def sel_fields(self):
        """
            Returns selected fields for edit_views
        """
        options = []
        fields = [ field.id for field in self.fields ]
        for field in Field.get_for_choices():
            if field[0] in fields:
                options.append("<option value='%s' selected>%s</option>" % (field[0],field[1]))
            else:
                options.append("<option value='%s'>%s</option>" % (field[0],field[1]))
        return options

class Category(PantotoBase):
    """
         Category Class
    """
    CATEGORY_TYPES = (
            ("pagelets","Pagelets LIst"),
            ("sitehome","Site Home"),
            ("sitemap","Site Map"),
            ("tree","Tree"),
            ("link","Link"),
    )
    name = StringField(max_length=100,required=True)
    slug = SlugField(max_length=100,help_text=_('Leave blank to auto generate'))
    description = StringField(max_length=255,help_text=_('Optional'))
    parent = ReferenceField('self')
    type = StringField(max_length = 255,choices=CATEGORY_TYPES)
    link = StringField(max_length=255)
    children_order = ListField(StringField(max_length=20),editable=False,default=[])
    disable_for_personas = ListField(ReferenceField(Persona),default=[],help_text=_('Disable this category in site for selected personas'))

    meta = {
        'collection': 'categories',
        'id_prefix' : 'cat',
        'slug_fields': (('slug','name'),),
        'verbose_name_plural': 'categories',
        'ordering': ['parent']
    }

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/c/%s/' % self.slug

    def is_disabled_for_user(self,user):
        if not hasattr(self,"disable for personas"):
            return False
        if not self.disable_for_personas:
            return False
        for persona in self.disable_for_personas:
            if user.belongs_to_persona(persona.id):
                return True
        return False

    def save(self,user=None,safe=True,force_insert=False):
        if not self.parent or self.parent == self:
            self.parent = None
        super(Category,self).save(user,safe,force_insert)

    def get_order_link(self):
        return '<a href="/admin/category/%s/order/" title="Order Children Categories"><img src="/static/base/images/icon_order.png" alt="Order" class="mid_align"/></a>' % self.id

    def get_children(self):
        if not self.children_order:
            return Category.objects(parent=self) 
        children = [ cat.id for cat in Category.objects(parent=self) ]
        if self.children_order:
            ordered = []
            for cat_id in self.children_order:
                if cat_id in children and cat_id not in ordered:
                    ordered.append(cat_id)
            for cat_id in children:
                if cat_id not in ordered:
                    ordered.append(cat_id)
        return [ Category.objects.get(id=cat_id) for cat_id in ordered ]

    def is_sitehome(self):
        return (self.type == "sitehome")

    def is_sitemap(self):
        return (self.type == "sitemap")

    def is_tree(self):
        return (self.type == "tree")

    def is_link(self):
        return (self.type == "link")

    def is_pagelets_list(self):
        return (self.type == "pagelets")

    def get_sitemap(self):
        for category in self.get_children():
            if category.is_sitemap():
                return category
        return None

class PageletProperty(EmbeddedDocument):
    """
        Pagelet Properties
    """
    PAGELET_TYPES = (
            ("normal","Normal"),
            ("post","Post"),
            ("form_only","Form Only"),
    )
    SUBMIT_OPTIONS = (
        ('default','Default'),
        ('attach_views','Attach Views')
    )
    prototype = BooleanField(default=False)
    form_title = StringField(max_length=255,help_text=_('Leave blank for default value "Post Pagelet"'))
    views = ListField(ReferenceField(View),default=[])
    categories = ListField(ReferenceField(Category),default=[])
    type = StringField(max_length = 20,choices=PAGELET_TYPES,default='normal')
    auto_title = BooleanField(default=False)
    title_template = StringField(max_length=255,required=False,help_text='Possible Variables:  {{user}}, {{title}}, {{date}}')
    on_submit = StringField(max_length = 20,choices=SUBMIT_OPTIONS,default='default')
    attach_views = ListField(ReferenceField(View),default=[])
    submit_once = BooleanField(default=False)
    submit_once_personas = ListField(ReferenceField(Persona),default=[])
    submit_once_message = StringField(max_length=255)
    field_order = ListField(StringField(max_length=20),editable=False,default=[])

class Pagelet(PantotoBase):
    """
        Pagelet Class
    """
    title = StringField(max_length=100,required=True)
    slug = SlugField(max_length=255,unique=True)
    description = TextField(required=False)
    opts = EmbeddedDocumentField(PageletProperty,editable=False,default=PageletProperty())
    post_data = DictField(editable=False,default={})
    authors = ListField(ReferenceField(User),editable=False,default=[])
    children = ListField(StringField(max_length=255),editable=False,default=[])

    meta = {
        'collection': 'pagelets',
        'id_prefix' : 'page',
        'slug_fields': ( ('slug','title'),)   
    }

    def __unicode__(self):
        return self.title

    def delete(self,safe=False):
        # Remove all child references
        for pagelet in Pagelet.objects:
            if self.id in pagelet.children:
                pagelet.children.remove(self.id)
                pagelet.save()
        super(PantotoBase,self).delete(safe)

    def add_author(self,author):
        if author not in self.authors:
            self.authors.append(author)
        return

    def add_child(self,child,save=False):
        if child.id and child.id not in self.children:
            self.children.append(child.id)
        if save:
            self.save()
        return

    def get_children(self):
        return [ Pagelet.objects.get(id=child) for child in self.children ]

    def get_prototype(self):
        return self.opts.prototype

    get_prototype.short_description = "Prototype"

    def get_views_list(self):
        if hasattr(self.opts,'views'):
            return ",".join([ view.name for view in self.opts.views ])
        else:
            return ""

    get_views_list.short_description = "Views"

    def get_categories(self):
        return ",".join([ category.name for category in self.opts.categories ])

    get_categories.short_description = "Categories"

    def get_admin_properties_link(self):
        return '<a href="/admin/pagelet/%s/properties/" title="Pagelet Properties"><img src="/static/base/images/icon_pagelet_property.png" alt="Properties" class="mid_align"/></a>' % self.id

    def get_admin_fields_order_link(self):
        return '<a href="/admin/pagelet/%s/order_fields/" title="Order Fields"><img src="/static/base/images/icon_order.png" alt="Order Fields" class="mid_align"/></a>' % self.id


class File(PantotoBase):
    """
        Pagelet Class
    """
    name = StringField(max_length=255,required=True,editable=False)
    description = StringField(max_length=255)
    path = StringField(max_length=255,required=True,editable=False)
    url = StringField(max_length=255,editable=False)
    size = IntField(editable=False)

    meta = {
        'collection': 'files',
        'id_prefix' : 'file'
    }

    def __unicode__(self):
        return self.name

    def get_file_link(self):
        return '<a href="%s" title="Download this file"><img src="/static/base/images/icon_download.png" alt="Download" class="mid_align"/></a>' % self.url

class Site(PantotoBase):
    """
        Site Class
    """
    name = StringField(max_length=80,required=True)
    slug = SlugField(max_length=80,help_text=_('Leave blank to auto generate'))
    description = StringField(max_length=255)
    category = ReferenceField(Category)
    logo = ReferenceField(File)

    meta = {
        'collection': 'sites',
        'id_prefix' : 'site',
        'slug_fields': (('slug','name'),)
    }

    def __unicode__(self):
        return self.name

    def save(self,user=None,safe=True,force_insert=False):
        if not self.category:
            self.category = None
        if not self.logo:
            self.logo = None
        super(Site,self).save(user,safe,force_insert)

    def get_view_site_link(self):
        return '<a href="/site/%s/" title="View Site" target="_blank"><img src="/static/base/images/icon_viewsite.png" alt="View"\
                                                class="mid_align"/></a>' % self.slug

    def get_logo_url(self):
        if self.logo:
            if os.path.exists(self.logo.url):
                return self.logo.url
        return '/static/base/images/logo.gif'

    def has_home_category(self):
        return bool(self.get_home_category())

    def get_home_category(self):
        if not self.category:
            return None
        home_category = self.category.get_sitemap()
        if not home_category:
            return None
        for sitemap in home_category.get_children():
            if sitemap.name.strip().lower() == "home":
                return sitemap
        return None

    def get_menu_items(self,current_link,user,link="",current_item_class="current_page_item"):
        category = self.category
        items = []
        if not category or category.is_disabled_for_user(user):
            return items
        if not category.is_sitehome() or not category.get_sitemap():
            return items
        for sitemap in category.get_sitemap().get_children():
            if sitemap.is_disabled_for_user(user):
                continue
            if sitemap.is_link():
                link = sitemap.link
            else:
                link = sitemap.get_absolute_url()
            if current_link == "/" and sitemap.name.lower().strip() == "home":
                klass = current_item_class
            elif link == current_link:
                klass = current_item_class
            else:
                klass = ""
            items.append("<li class='%s'><a href='%s' title='%s'>%s</a></li>" % (klass,link,sitemap.description,sitemap.name))
        return "\n".join(items)


class Theme(PantotoBase):
    THEME_TYPES = (
        ('site','Site Theme'),
        ('admin','Admin Theme'),
    )
    name = StringField(max_length=40,required=True)
    slug = SlugField(max_length=40,required=True)
    description = StringField(max_length=100)
    thumbnail = StringField(max_length=100)
    type = StringField(max_length=10,choices=THEME_TYPES,required=True)

    meta = {
        'collection': 'themes',
        'id_prefix' : 'theme',
    }

    def __unicode__(self):
        return self.name

    def is_site_theme(self):
        return self.type == 'site'

    def get_media_path(self):
        if self.is_site_theme():
            return "%s%s" % (settings.SITE_THEME_URL,self.slug)
        else:
            return "%s%s" % (settings.ADMIN_THEME_URL,self.slug)

    def get_base(self):
        return 'themes/%s/%s/index.html' % (self.type,self.slug)

    def get_login_base(self):
        return 'themes/%s/%s/login.html' % (self.type,self.slug)

    @classmethod
    def get_for_choices(cls,theme_type="admin"):
        """
            Returns tuple (id,object name) for choice field choices
        """
        if theme_type == "admin":
            return  [ (theme.id,theme.name) for theme in cls.objects(type='admin') ]
        else:
            return  [ (theme.id,theme.name) for theme in cls.objects(type='site') ]

class UserSetting(PantotoBase):
    user = ReferenceField(User)
    site = ReferenceField(Site)
    site_theme = ReferenceField(Theme)
    admin_theme = ReferenceField(Theme)

    meta = {
        'collection': 'settings',
        'id_prefix' : 'setting',
    }

    def __unicode__(self):
        return self.user.username


