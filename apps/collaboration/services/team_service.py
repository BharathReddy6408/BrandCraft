from collaboration.models import TeamMember, Invitation, Role
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class TeamService:
    @staticmethod
    def invite_member(project, email, role, inviter):
        # Create invitation
        invitation = Invitation.objects.create(
            project=project,
            email=email,
            role=role,
            invited_by=inviter
        )
        # TODO: send email
        return invitation
        
    @staticmethod
    def accept_invitation(token, user):
        try:
            invitation = Invitation.objects.get(token=token, status='PENDING')
        except Invitation.DoesNotExist:
            return False, "Invalid or expired invitation."
            
        if invitation.email != user.email:
            return False, "Email mismatch."
            
        TeamMember.objects.get_or_create(
            project=invitation.project,
            user=user,
            defaults={'role': invitation.role}
        )
        
        invitation.status = 'ACCEPTED'
        invitation.save()
        return True, invitation.project
        
    @staticmethod
    def revoke_invitation(invitation_id, user):
        try:
            invitation = Invitation.objects.get(id=invitation_id)
            invitation.status = 'REVOKED'
            invitation.save()
            return True
        except Invitation.DoesNotExist:
            return False
            
    @staticmethod
    def remove_member(project, user_id):
        TeamMember.objects.filter(project=project, user_id=user_id).delete()
        return True
