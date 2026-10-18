from rest_framework.permissions import BasePermission


class IsGroupOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class IsGroupOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner_id == request.user.id:
            return True
        return obj.members.filter(user=request.user,role="admin",).exists()


