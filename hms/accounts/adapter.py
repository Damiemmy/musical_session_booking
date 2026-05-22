from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        This is where we link existing Django users
        to Google accounts based on email.
        """

        if sociallogin.is_existing:
            return

        user = sociallogin.user

        if not user.email:
            return

        try:
            existing_user = User.objects.get(email=user.email)

            # KEY LINE: connect Google account to existing user
            sociallogin.connect(request, existing_user)

        except User.DoesNotExist:
            pass