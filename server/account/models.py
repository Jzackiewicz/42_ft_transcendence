from django.db import models
from django.contrib.auth.models import AbstractUser

# authentication(login, permisiions, passwords)
class User(AbstractUser):
    """
    User model extending Django's AbstractUser,
    it can be extended later without painful migrations
    """
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.username

# person (avatar, online, friends etc)
class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_online = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', blank=True) # django created a hidden table for it

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self) -> str:
        return f"{self.user.username}'s profile"
