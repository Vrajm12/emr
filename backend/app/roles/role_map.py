ROLES = {
    "SYSTEM_ADMIN": {
        "name": "System Admin",
        "permissions": [
            "tenant:view",
            "tenant:update",
            "audit:view"
        ]
    },
    "CLINIC_ADMIN": {
        "name": "Clinic Admin",
        "permissions": [
            "user:create",
            "user:view",
            "user:update",
            "audit:view"
        ]
    },
    "DOCTOR": {
        "name": "Doctor",
        "permissions": [
            "user:view"
        ]
    },
    "NURSE": {
        "name": "Nurse",
        "permissions": [
            "user:view"
        ]
    },
    "RECEPTIONIST": {
        "name": "Receptionist",
        "permissions": [
            "user:view"
        ]
    },
    "COMPLIANCE_OFFICER": {
        "name": "Compliance Officer",
        "permissions": [
            "audit:view"
        ]
    }
}
