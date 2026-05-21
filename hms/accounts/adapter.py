from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        # THIS FORCE LINKS EXISTING EMAIL USERS
        if sociallogin.is_existing:
            return

        user = sociallogin.user
        if user.email:
            user.username = user.email.split("@")[0]