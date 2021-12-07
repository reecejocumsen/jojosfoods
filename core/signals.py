from allauth.account.signals import user_signed_up
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out, user_logged_in


def logout_notifier(sender, request, user, **kwargs):
    messages.info(request, "You have successfully logged out.",
                  extra_tags="alert-success")


def login_notifier(sender, request, user, **kwargs):
    messages.info(request, "You have successfully logged in. Hi, {0}!".format(user.username),
                  extra_tags="alert-success")


user_logged_out.connect(logout_notifier)
user_logged_in.connect(login_notifier)
