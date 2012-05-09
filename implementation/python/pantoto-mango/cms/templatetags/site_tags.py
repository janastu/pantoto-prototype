from django import template
from django.template import Library,Node,Variable
from pantoto.models import Site

register = Library()

class DisplaySiteMenuNode(Node):

    def __init__(self,site,user,current_path):
        self.site = site
        self.current_path = current_path
        self.user = user

    def render(self,context):
        site = Variable(self.site).resolve(context)
        current_path = Variable(self.current_path).resolve(context)
        user = Variable(self.user).resolve(context)
        return site.get_menu_items(current_path,user)

@register.tag
def display_site_menu(parser,token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name,site,user,current_path = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" %token.contents.split()[0]
    return DisplaySiteMenuNode(site,user,current_path)

