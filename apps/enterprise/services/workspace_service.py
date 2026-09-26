from enterprise.models import AssetCollection, CollectionItem, WorkspaceItemMeta, ChangeHistory
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class WorkspaceService:
    @staticmethod
    def toggle_favorite(user, project, item):
        ct = ContentType.objects.get_for_model(item)
        meta, created = WorkspaceItemMeta.objects.get_or_create(
            user=user, project=project, content_type=ct, object_id=item.id
        )
        meta.is_favorite = not meta.is_favorite
        meta.save()
        return meta.is_favorite
        
    @staticmethod
    def toggle_pin(user, project, item):
        ct = ContentType.objects.get_for_model(item)
        meta, created = WorkspaceItemMeta.objects.get_or_create(
            user=user, project=project, content_type=ct, object_id=item.id
        )
        meta.is_pinned = not meta.is_pinned
        meta.save()
        return meta.is_pinned

    @staticmethod
    def mark_accessed(user, project, item):
        ct = ContentType.objects.get_for_model(item)
        meta, created = WorkspaceItemMeta.objects.get_or_create(
            user=user, project=project, content_type=ct, object_id=item.id
        )
        meta.last_accessed = timezone.now()
        meta.save()
        return meta
        
    @staticmethod
    def create_collection(project, name, user, description=None):
        return AssetCollection.objects.create(
            project=project, name=name, description=description, created_by=user
        )
        
    @staticmethod
    def add_to_collection(collection, item):
        ct = ContentType.objects.get_for_model(item)
        CollectionItem.objects.get_or_create(
            collection=collection, content_type=ct, object_id=item.id
        )
        
    @staticmethod
    def log_change(project, user, action, item, previous_value=None, current_value=None):
        ct = ContentType.objects.get_for_model(item) if item else None
        ChangeHistory.objects.create(
            project=project,
            user=user,
            action=action,
            content_type=ct,
            object_id=item.id if item else None,
            previous_value=previous_value,
            current_value=current_value
        )
