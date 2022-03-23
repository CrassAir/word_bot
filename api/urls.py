from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from django.conf import settings

router = routers.DefaultRouter()
# router.register('account', views.AccountShortViewSet, 'account')

urlpatterns = [
    path('', include(router.urls)),
    # path('all/', views.home_data_view, name="api_home_data"),
    # path('test/', views.update_photo_catalog, name='update_photo_catalog'),
    # path('cartridges-and-supplies/', views.cartridge_and_supply_data_view),
]
urlpatterns += static('voices/', document_root=settings.MEDIA_ROOT)
