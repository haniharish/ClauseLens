"""
ClauseLens – Account-level permissions (kept here for accounts app).
Shared permissions live in apps.common.permissions.
"""
from apps.common.permissions import IsOwner, IsInternalService  # re-export

__all__ = ['IsOwner', 'IsInternalService']
