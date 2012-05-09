
class AdminBase(object):
    """
        list_display = {'cols':(),'actions':()}
        custom_buttons = (
              {'label':'':'dest':'','set_val':'','redirect':''}
        )
        class Media:
            js = ()
            css = ()
    """
    pass

class UserAdmin(AdminBase):
   list_display = {'cols':('username','first_name','last_name','email','is_active')}

class PersonaAdmin(AdminBase):
    list_display = {'cols':('name','description','get_users_list')}

class FileAdmin(AdminBase):
    list_display = {'cols':('name','description','size'),'actions':('get_file_link',)}

class SiteAdmin(AdminBase):
    list_display = {'cols':('name','slug','description','get_category_name'),'actions':('get_view_site_link',)}

class CategoryAdmin(AdminBase):
    list_display = {'cols':('name','slug','description','get_type','get_parent_name'),'actions':('get_order_link',)}

    class Media:
        js = ('/static/base/js/treeTable/jquery.treeTable.js','/static/base/js/admin/category.js')
        css = ('/static/base/js/treeTable/jquery.treeTable.css',)

class FieldAdmin(AdminBase):
    list_display = {'cols':('label','get_type','required')}

    class Media:
        js = ('/static/base/js/admin/field.js',)

class ViewAdmin(AdminBase):
    list_display = {'cols':('name','description','get_pagelets_link')}

    class Media:
        js = ('/static/base/js/jquery.selectboxes.js','/static/base/js/admin/view.js',)

class PageletAdmin(AdminBase):
    list_display = {'cols':('title','get_prototype','slug','get_views_list','get_categories'),\
                    'actions':('get_admin_properties_link','get_admin_fields_order_link')}

    custom_buttons = (
              {'label':'Save as Prototype','dest':'prototype','set_val':True},
    )

    redirect_button = (
            {'Save and set Properties':'/admin/pagelet/$id/properties/'},
    )
    
    class Media:
        js = ('/static/base/js/jwysiwyg/jquery.wysiwyg.js','/static/base/js/admin/pagelet.js',)
        css = ('/static/base/js/jwysiwyg/jquery.wysiwyg.css',)

class PageletPropertyAdmin(AdminBase):

    class Media:
        js = ('/static/base/js/admin/pagelet_property.js',)

