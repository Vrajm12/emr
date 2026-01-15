from app.roles.role_map import ROLES

def get_permissions_for_role(role_name: str):
    role = ROLES.get(role_name)
    if not role:
        return []

    return role.get("permissions", [])

def has_permission(role_name: str, permission: str) -> bool:
    permissions = get_permissions_for_role(role_name)
    return permission in permissions
