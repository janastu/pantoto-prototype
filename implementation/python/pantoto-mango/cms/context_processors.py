from pantoto import Pantoto

def common_context(request):
    user = request.user	
    site,site_theme,admin_theme = Pantoto().get_current_site(request)
    return {'site':site,'site_theme':site_theme,'admin_theme':admin_theme,'admin_base':admin_theme.get_base(),'site_base':site_theme.get_base(),\
            'site_login_base':site_theme.get_login_base(),'admin_login_base':admin_theme.get_login_base()}
   
