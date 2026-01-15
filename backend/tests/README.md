# Authentication & Security Test Suite

## Test Cases

### TC-01: Valid Login
**Description**: Valid Login with valid email/password

**Expected Outcomes**:
1. JWT token is returned
2. Session is created in the database
3. Audit event is logged with action: `LOGIN_SUCCESS`

### TC-02: Invalid Password
**Description**: Login attempt with wrong password

**Expected Outcomes**:
1. 401 Unauthorized returned
2. No session created
3. Audit event is logged with action: `LOGIN_FAILED`

### TC-03: Token Tampering
**Description**: Modify JWT payload and send request

**Expected Outcomes**:
1. 401 Unauthorized returned
2. Audit event is logged with action: `TOKEN_INVALID`

### TC-04: Token Expiry
**Description**: Use expired JWT token

**Expected Outcomes**:
1. 401 Unauthorized returned
2. Audit event is logged with action: `TOKEN_EXPIRED`

## Running the Tests

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test cases
```bash
# TC-01: Valid Login
pytest tests/test_auth.py::TestTC01ValidLogin -v

# TC-02: Invalid Password
pytest tests/test_security.py::TestTC02InvalidPassword -v

# TC-03: Token Tampering
pytest tests/test_security.py::TestTC03TokenTampering -v

# TC-04: Token Expiry
pytest tests/test_security.py::TestTC04TokenExpiry -v
```

### Run with output
```bash
pytest tests/ -v -s
```

### Run with coverage
```bash
pytest tests/ --cov=app.auth --cov=app.core -v
```

## Test Results Summary

### TC-01: Valid Login ✅
- `test_valid_login_returns_jwt` - Verifies JWT is returned
- `test_valid_login_creates_session` - Verifies session creation
- `test_valid_login_logs_audit_event` - Verifies audit event logging
- `test_full_login_flow_integration` - Full integration test

### TC-02: Invalid Password ✅
- `test_invalid_password_returns_401` - Verifies 401 status
- `test_invalid_password_no_session_created` - Verifies no session
- `test_invalid_password_logs_audit_event` - Verifies LOGIN_FAILED event

### TC-03: Token Tampering ✅
- `test_tampered_token_returns_401` - Verifies rejection of tampered token
- `test_tampered_token_logs_audit_event` - Verifies TOKEN_INVALID event

### TC-04: Token Expiry ✅
- `test_expired_token_returns_401` - Verifies rejection of expired token
- `test_expired_token_logs_audit_event` - Verifies TOKEN_EXPIRED event
- `test_expired_token_full_flow` - Full integration test

## Implementation Changes

### Modified Files
1. [backend/app/auth/routes.py](../app/auth/routes.py) - Added audit logging for failed logins
2. [backend/app/core/jwt_middleware.py](../app/core/jwt_middleware.py) - Added audit logging for token errors
3. [backend/app/core/security.py](../app/core/security.py) - Fixed JWT_SECRET_KEY reference
4. [backend/tests/test_auth.py](test_auth.py) - TC-01 test suite
5. [backend/tests/test_security.py](test_security.py) - TC-02, TC-03, TC-04 test suites
6. [backend/tests/conftest.py](conftest.py) - Test fixtures and configuration
7. [backend/requirements.txt](../requirements.txt) - Added test dependencies

## Test Environment
- Python 3.14
- pytest 9.0.2
- pytest-asyncio 1.3.0
- FastAPI with async support
