from django import forms
from pantoto.models import User

def clean_password(self):
    if self.data['password'] != self.data['confirm_password']:
        raise forms.ValidationError('Passwords do not match')
    return self.data['password']

class BaseForm(object):
    """
    extra_fields = {}
    clean_methods = ()
    field_order = ()
    """
    pass

class UserForm(BaseForm):
    extra_fields = {
        'confirm_password': forms.CharField(widget=forms.PasswordInput(render_value=False))
    }
    clean_methods = ('clean_password',)
    field_order = ('username','password','confirm_password','first_name','last_name','email','is_staff','is_active','is_superuser')

class EditUserForm(BaseForm):
    exclude_fields = ('password',)
    field_order = ('username','first_name','last_name','email','is_staff','is_active','is_superuser')

class PersonaForm(BaseForm):
    field_order = ('name','description','users')

class FieldForm(BaseForm):
    field_order = ('label','type','required','help_text','initial','choices','max_length','rows','cols')

class ViewForm(BaseForm):
    field_order = ('name','description','fields')
    
class PageletForm(BaseForm):
    field_order = ('title','description')

class PageletPropertyForm(BaseForm):
    field_order = ('prototype','form_title','views','categories','type','auto_title','title_template','on_submit','attach_views','submit_once',\
                    'submit_once_personas','submit_once_message')

class CategoryForm(BaseForm):
    field_order = ('name','slug','description','parent','type','link','disable_for_personas')

class SiteForm(BaseForm):
    field_order = ('name','slug','description','category')
    
class FileForm(forms.Form):
    _file  = forms.FileField(label='File')
    description = forms.CharField(max_length=255,required=False,help_text='Optional')

class EditFileForm(forms.Form):
    description = forms.CharField(max_length=255,required=False,help_text='Optional')

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    password         = forms.CharField(widget=forms.PasswordInput(render_value=False))
    confirm_password = forms.CharField(widget=forms.PasswordInput(render_value=False))

    def __init__(self,user,*args,**kwargs):
        self.user = user 
        super(ChangePasswordForm,self).__init__(*args,**kwargs)

    def clean_current_password(self):
        if self.data.get('current_password') and not self.user.check_password(self.data['current_password']):
            raise forms.ValidationError('Incorrect current password.')
        return self.data['current_password']

    def clean_password(self):
        if self.data['current_password'] == self.data['password']:
            raise forms.ValidationError('Current Password and New Password can\'t be the same')
        if self.data['password'] != self.data['confirm_password']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

    def clean(self,*args, **kwargs):
       return super(ChangePasswordForm, self).clean(*args, **kwargs)
