from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.paginations import CustomPageNumberPaginator
from .models import Follow, User
from .serializers import (CreateFollowSerializer, SubscriptionsSerializer,
                          UserSerializer)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPaginator

    def get_queryset(self):
        if self.action == 'following_list':
            return User.objects.filter(following__user=self.request.user)
        return self.queryset

    @action(detail=True,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        follower = Follow.objects.values_list(
            'author__username').filter(user=request.user)
        queryset = User.objects.filter(username__in=follower)
        pages = self.paginate_queryset(queryset)
        context = {'request': request}
        serializer = SubscriptionsSerializer(pages,
                                             many=True,
                                             context=context)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        following = get_object_or_404(User, pk=pk)
        follower = request.user
        data = {'user': follower.id,
                'author': following.id}
        context = {'request': request}
        serializer = CreateFollowSerializer(data=data,
                                            context=context)
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        get_object_or_404(Follow,
                          user=request.user,
                          author=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
