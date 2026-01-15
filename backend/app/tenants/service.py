from app.tenants.repository import TenantRepository
from app.users.repository import UserRepository
from app.core.security import hash_password

async def create_tenant(db, name: str, contact_email: str, admin_password: str):
    tenant_repo = TenantRepository(db)
    user_repo = UserRepository(db)

    # Prevent duplicates
    existing = await tenant_repo.find_by_name(name)
    if existing:
        return None

    # Create tenant
    tenant = await tenant_repo.create({
        "name": name,
        "status": "active",
        "contact_email": contact_email
    })

    # Create first clinic admin
    admin_user = await user_repo.create({
        "tenant_id": tenant["_id"],
        "email": contact_email,
        "password_hash": hash_password(admin_password),
        "role_name": "CLINIC_ADMIN",
        "is_active": True
    })

    return {
        "tenant": tenant,
        "admin_user": admin_user
    }
