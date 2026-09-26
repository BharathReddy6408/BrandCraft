from enterprise.models import SharedLink
from django.contrib.contenttypes.models import ContentType

class SharingService:
    @staticmethod
    def create_shared_link(project, user, item=None, expires_in_days=7, password=None):
        link = SharedLink(
            project=project,
            created_by=user
        )
        if item:
            link.content_type = ContentType.objects.get_for_model(item)
            link.object_id = item.id
            
        if password:
            # Simple hash for MVP
            import hashlib
            link.password_hash = hashlib.sha256(password.encode()).hexdigest()
            
        link.save()
        return link
        
    @staticmethod
    def verify_password(link, password):
        if not link.password_hash:
            return True
        import hashlib
        return link.password_hash == hashlib.sha256(password.encode()).hexdigest()
