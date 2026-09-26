from workflow.models import ApprovalItem, ContentVersion
from django.contrib.contenttypes.models import ContentType
from activitylogs.models import ActivityLog

class ApprovalService:
    @staticmethod
    def queue_for_approval(project, user, instance, item_type, title, payload):
        """
        Takes a generated model instance (e.g. SocialPost), wraps it in an ApprovalItem,
        and saves its initial version.
        """
        content_type = ContentType.objects.get_for_model(instance)
        
        # Check if an approval item already exists for this object
        approval, created = ApprovalItem.objects.get_or_create(
            project=project,
            content_type=content_type,
            object_id=instance.id,
            defaults={
                'user': user,
                'item_type': item_type,
                'title': title,
                'status': 'PENDING'
            }
        )
        
        # If it wasn't created, ensure it goes back to PENDING if we are queuing a regeneration
        if not created:
            approval.status = 'PENDING'
            approval.save()
            
        # Determine version number
        latest_version = approval.versions.order_by('-version_number').first()
        version_num = (latest_version.version_number + 1) if latest_version else 1
        
        # Create version
        ContentVersion.objects.create(
            approval_item=approval,
            version_number=version_num,
            payload=payload
        )
        
        ActivityLog.objects.create(
            project=project,
            user=user,
            action=f"Queued {item_type} for Approval",
            description=f"Generated version {version_num} of {title}"
        )
        
        return approval

    @staticmethod
    def approve_item(approval_item, user):
        approval_item.status = 'APPROVED'
        approval_item.save()
        
        ActivityLog.objects.create(
            project=approval_item.project,
            user=user,
            action=f"Approved {approval_item.item_type}",
            description=f"Approved: {approval_item.title}"
        )
        return approval_item

    @staticmethod
    def reject_item(approval_item, user, feedback=""):
        approval_item.status = 'REJECTED'
        approval_item.feedback = feedback
        approval_item.save()
        
        ActivityLog.objects.create(
            project=approval_item.project,
            user=user,
            action=f"Rejected {approval_item.item_type}",
            description=f"Rejected: {approval_item.title} with feedback: {feedback}"
        )
        return approval_item
