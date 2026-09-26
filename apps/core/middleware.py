from django.utils import timezone
from django.conf import settings

class ActivityTrackingMiddleware:
    """
    Middleware to track user activity and update last_login_ip.
    In the future, this will connect to the activitylogs app to record 
    specific page views and actions if needed.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # After response is processed, track user activity if authenticated
        if request.user.is_authenticated:
            # We can get the user's IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Update user's last known IP if changed (to prevent too many writes, 
            # we might only update if it differs, or track in login view instead, 
            # but doing it here ensures it's always current).
            # For performance, updating every request is heavy, so we might
            # just rely on Django's built in last_login for the timestamp.
            # We'll just capture it in session for now.
            request.session['last_ip'] = ip
            
        return response
