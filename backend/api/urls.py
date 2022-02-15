from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register(r'^recipes', RecipeViewSet, 'recipes')

urlpatterns = [
    path('users/subscriptions/',
         UserViewSet.as_view({'get': 'subscriptions'}),
         name='subscriptions'),
    path('users/<int:pk>/subscribe/',
         UserViewSet.as_view({'post': 'subscribe',
                              'delete': 'subscribe'})),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
