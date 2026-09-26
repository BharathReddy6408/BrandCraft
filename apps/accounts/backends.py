from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend to allow users to log in using either their
    username or their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            
        try:
            # Try to fetch the user by searching the username or email field
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            
            # Check the password
            if user.check_password(password):
                # Verify if user is locked out
                if user.is_locked:
                    return None
                    
                # Reset failed login attempts on successful login
                if user.failed_login_attempts > 0:
                    user.failed_login_attempts = 0
                    user.save(update_fields=['failed_login_attempts'])
                    
                return user
            else:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5: # Lock account after 5 failed attempts
                    user.is_locked = True
                user.save(update_fields=['failed_login_attempts', 'is_locked'])
                
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user.
            User().set_password(password)
            return None
