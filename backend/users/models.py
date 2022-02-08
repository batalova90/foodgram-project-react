from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True
    )
    password = models.CharField(
        max_length=150,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name',
                       'last_name',
                       'username']

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return self.author.username
