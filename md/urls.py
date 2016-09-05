"""md URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from kd import views as kd_views
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('users.urls'), name='account'),
    #url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html'), name='user_profile'),
    url(r'^$', kd_views.home, name='home'),
    url(r'^login/', kd_views.login, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^profile/', kd_views.user_profile, name='user_profile'),
    url(r'^user_profile/$', RedirectView.as_view(url='/profile/?order_type=all&time=create_time&asc=0&page=1')),
    url(r'^create/', kd_views.create, name='create'),
    url(r'^create_order/', kd_views.create_order, name='create_order'),
    url(r'^search_order/', kd_views.search_order, name='search_order'),
    url(r'^order_info/', kd_views.order_info_insider, name='order_info'),
    url(r'^order_update_call/', kd_views.order_update_call, name='order_update_call'),
    url(r'^order_update/', kd_views.order_update, name='order_update'),
    # url(r'^ajax_inital/$', kd_views.ajax_get_inital_order, name='ajax-inital'),
    # url(r'^ajax_shipping/$', kd_views.ajax_get_shipping_order, name='ajax-shipping'),
    # url(r'^ajax_delivered/$', kd_views.ajax_get_delivered_order, name='ajax-delivered'),
    # url(r'^ajax_all/$', kd_views.ajax_get_all_order, name='ajax-all'),
    url(r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            kd_views.reset_confirm, name='reset_confirm'),
    url(r'^reset/$', kd_views.reset, name='reset'),
    url(r'^create_quote/', kd_views.create_quote, name='create_quote'),
    url(r'^quote/', kd_views.quote, name='quote'),
    url(r'^order_info_edit_show/', kd_views.edit_order_info_show, name='edit_order_info_show'),
    url(r'^edit_order_info/', kd_views.edit_order_info, name='edit_order_info'),
    url(r'^external_order_info_edit_show/', kd_views.edit_external_order_info_show, name='edit_external_order_info_show'),
    url(r'^edit_external_order_info/', kd_views.edit_external_order_info, name='edit_external_order_info'),
    ]

