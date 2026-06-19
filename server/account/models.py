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

# person (avatar, friends etc)
class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self) -> str:
        return f"{self.user.username}'s profile"
    
    def avatar_url(self, request=None) -> str | None:
        if not self.avatar:
            return None
        url = self.avatar.url
        return request.build_absolute_uri(url) if request else url
    
# links django user to an external OAuth identity
class SocialAccount(models.Model):
    PROVIDER_GOOGLE = "google"
    PROVIDER_CHOICES = [(PROVIDER_GOOGLE, "Google")]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="social_accounts",
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    uid = models.CharField(max_length=255)  # provider's stable user id (Google's 'sub')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "uid")
        indexes = [models.Index(fields=("provider", "uid"))]
        verbose_name = "Social Account"
        verbose_name_plural = "Social Accounts"

    def __str__(self) -> str:
        return f"{self.user.username} via {self.provider}"
