from django.urls import path

from .views import UserViewSet

urlpatterns = [
        path('users/subscriptions/',
             UserViewSet.as_view({'get': 'subscriptions'}),
             name='subscriptions'),

]
