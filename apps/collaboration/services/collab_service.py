from collaboration.models import ProjectTask, Comment
from django.contrib.contenttypes.models import ContentType

class CollaborationService:
    @staticmethod
    def create_task(project, creator, title, description=None, assignee=None, priority='MEDIUM', due_date=None, related_item=None):
        task = ProjectTask(
            project=project,
            created_by=creator,
            title=title,
            description=description,
            assignee=assignee,
            priority=priority,
            due_date=due_date
        )
        if related_item:
            task.content_type = ContentType.objects.get_for_model(related_item)
            task.object_id = related_item.id
            
        task.save()
        return task
        
    @staticmethod
    def update_task_status(task_id, status):
        task = ProjectTask.objects.get(id=task_id)
        task.status = status
        task.save()
        return task

    @staticmethod
    def add_comment(project, author, text, target_item, parent_id=None):
        comment = Comment(
            project=project,
            author=author,
            text=text,
            content_type=ContentType.objects.get_for_model(target_item),
            object_id=target_item.id
        )
        if parent_id:
            comment.parent_id = parent_id
        comment.save()
        return comment
