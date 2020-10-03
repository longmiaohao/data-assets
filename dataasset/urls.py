"""dataasset URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
# from api import views as api_view
from django.views.generic.base import RedirectView
from index import views as index_view
from sjgxgk import views as sjgxgk_view
from process import views as process_view

urlpatterns = [
    # url(r'^crud/(?P<value>\d*)$', api_view.dispatch_by_method, name="dispatch"),
    # url(r'^platform/add', api_view.platform_insert, name="platform_insert"),
    url(r"xtda_data", index_view.xtda_data, name="xtda_data"),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r"xtda_delete", index_view.xtda_delete, name="xtda_delete"),
    url(r"xtda_add", index_view.xtda_add, name="xtda_add"),
    url(r"xtda_edit", index_view.xtda_edit, name="xtda_edit"),
    url(r"autocomplete", index_view.get_dw_xm_by_zgh, name="autocomplete"),
    url(r"yhda_add", index_view.yhda_add, name="yhda_add"),
    url(r"yhda_edit", index_view.yhda_edit, name="yhda_edit"),
    url(r"yhda_delete", index_view.yhda_delete, name="yhda_delete"),
    url(r"yhda_decrypt", index_view.yhda_decrypt, name="yhda_decrypt"),
    url(r"yhda_ssxtyh", index_view.yhda_ssxtyh, name="yhda_ssxtyh"),
    url(r"yhda", index_view.yhda_index, name="yhda_index"),
    url(r"xtda", index_view.xtda_index, name="xtda_index"),
    url(r"xxsj", sjgxgk_view.xxsj, name="xxsj"),
    url(r"processcard", process_view.index, name="process_index"),
    url(r"apply", process_view.apply, name="process_apply"),
    url(r"review", process_view.review, name="process_review"),
    url(r"tabledetail", process_view.tabledetail, name="process_tabledetail"),
    url(r"", sjgxgk_view.index_old, name="sjgxgk_index"),
]
