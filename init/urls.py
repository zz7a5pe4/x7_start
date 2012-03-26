from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^submit_env$', 'init.views.submit_env'),
    (r'^get_progress', 'init.views.get_progress'),
    (r'^$', 'init.views.home'),
    # Examples:
    # url(r'^$', 'x7_start.views.home', name='home'),
    # url(r'^x7_start/', include('x7_start.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
