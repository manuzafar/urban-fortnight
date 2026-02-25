# API Integration Test Checklist

Use this checklist when developing or reviewing API endpoints.

## For Every New Endpoint

### 1. Authentication Tests
- [ ] Returns 401/403 without authentication
- [ ] Returns 401/403 with invalid token
- [ ] Returns 200/20x with valid token
- [ ] Verifies user ownership of resources

### 2. Validation Tests
- [ ] Returns 422 for missing required fields
- [ ] Returns 422 for invalid field types
- [ ] Returns 422 for out-of-range values
- [ ] Returns 422 for too short/long strings
- [ ] Accepts valid inputs

### 3. Error Handling Tests
- [ ] Returns 404 for non-existent resources
- [ ] Returns 400 for bad requests
- [ ] Returns 500 errors gracefully
- [ ] Returns appropriate error messages
- [ ] Logs errors properly

### 4. Success Cases
- [ ] Returns correct status code (200, 201, 202, 204)
- [ ] Returns correct response schema
- [ ] Returns all required fields
- [ ] Returns correct data types

### 5. Database Tests (if applicable)
- [ ] Creates records correctly
- [ ] Reads records correctly
- [ ] Updates records correctly
- [ ] Deletes records correctly
- [ ] Handles concurrent operations

### 6. Business Logic Tests
- [ ] Validates business rules
- [ ] Handles edge cases
- [ ] Processes data correctly
- [ ] Updates related resources

## For V4 Discovery Endpoints

### Session Management
- [ ] Creates session with valid mode
- [ ] Loads session from cache
- [ ] Loads session from database
- [ ] Persists session to database
- [ ] Updates session state

### Stage Execution
- [ ] Runs stage successfully
- [ ] Updates stage status to in_progress
- [ ] Marks stage as completed
- [ ] Handles stage errors
- [ ] Persists stage output
- [ ] Validates stage names
- [ ] Prevents invalid stage transitions

### Interview Management
- [ ] Adds interviews
- [ ] Updates evidence quality
- [ ] Synthesizes patterns
- [ ] Validates interview data
- [ ] Handles multiple interviews

### Lifecycle Continuation
- [ ] Validates prerequisites
- [ ] Queues background task
- [ ] Emits SSE events
- [ ] Handles continuation errors

## Test Quality Checklist

### Code Quality
- [ ] Test has clear, descriptive name
- [ ] Test has docstring
- [ ] Test is isolated (no dependencies)
- [ ] Test uses appropriate fixtures
- [ ] Test mocks external dependencies
- [ ] Test assertions are clear

### Coverage
- [ ] Test covers happy path
- [ ] Test covers error paths
- [ ] Test covers edge cases
- [ ] Test covers security concerns
- [ ] Test achieves >85% line coverage

### Performance
- [ ] Test runs in <0.1s
- [ ] Test doesn't make real API calls
- [ ] Test doesn't access real database
- [ ] Test doesn't make LLM calls

### Maintenance
- [ ] Test is documented
- [ ] Test uses shared fixtures
- [ ] Test follows existing patterns
- [ ] Test is easy to understand

## Running Tests Checklist

Before committing:
- [ ] Run all integration tests: `pytest tests/integration/test_api_endpoints.py -v`
- [ ] All tests pass
- [ ] No warnings
- [ ] Coverage is >85%: `pytest tests/integration/test_api_endpoints.py --cov=main --cov=api --cov-report=term`

Before merging:
- [ ] CI pipeline passes
- [ ] Code review approved
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)

## Security Checklist

### Input Sanitization
- [ ] Tests XSS prevention
- [ ] Tests SQL injection prevention
- [ ] Tests path traversal prevention
- [ ] Tests command injection prevention

### Authentication & Authorization
- [ ] Tests missing auth
- [ ] Tests invalid auth
- [ ] Tests expired tokens
- [ ] Tests ownership verification
- [ ] Tests role-based access

### Data Protection
- [ ] Tests sensitive data masking
- [ ] Tests proper error messages (no leaks)
- [ ] Tests rate limiting (if applicable)

## Endpoint-Specific Checklists

### POST /api/discovery/start
- [ ] Requires authentication
- [ ] Validates product_idea (min 30 chars, max 2000 chars)
- [ ] Validates optional fields
- [ ] Handles max concurrent sessions
- [ ] Creates session in database
- [ ] Returns session_id
- [ ] Queues background task
- [ ] Sanitizes inputs

### GET /api/discovery/session/{id}
- [ ] Requires authentication
- [ ] Verifies ownership
- [ ] Returns 404 for non-existent
- [ ] Returns session status
- [ ] Includes inception_pack if completed
- [ ] Returns proper error states

### POST /api/discovery/v4/test/sessions
- [ ] Validates product_idea (min 30 chars)
- [ ] Validates mode (quick/guided/deep)
- [ ] Creates session without auth (test endpoint)
- [ ] Persists to database
- [ ] Returns session_id and mode
- [ ] Initializes all 5 stages

### POST /api/discovery/v4/test/sessions/{id}/stages/{stage}/run
- [ ] Validates session exists
- [ ] Validates stage name
- [ ] Updates stage status to in_progress
- [ ] Queues background task
- [ ] Persists state
- [ ] Returns immediately
- [ ] Handles LLM errors

### POST /api/discovery/v4/test/sessions/{id}/interviews
- [ ] Validates interview data
- [ ] Creates interview record
- [ ] Updates evidence quality
- [ ] Persists to database
- [ ] Returns interview with ID

### POST /api/discovery/v4/test/sessions/{id}/continue-to-strategy
- [ ] Validates at least one stage completed
- [ ] Queues full lifecycle
- [ ] Returns immediately
- [ ] Handles errors gracefully

## Example Test Template

```python
class TestNewEndpoint:
    """Tests for POST /api/new/endpoint."""

    def test_requires_auth(self, test_client):
        """Endpoint should require authentication."""
        response = test_client.post("/api/new/endpoint")
        assert response.status_code in [401, 403]

    def test_validates_required_fields(self, test_client, auth_headers, test_user_id):
        """Endpoint should validate required fields."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            response = test_client.post(
                "/api/new/endpoint",
                json={},
                headers=auth_headers,
            )
        assert response.status_code == 422

    def test_success(self, test_client, auth_headers, test_user_id):
        """Endpoint should process valid requests."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.create.return_value = None

            response = test_client.post(
                "/api/new/endpoint",
                json={"field": "value"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data

    def test_handles_errors(self, test_client, auth_headers, test_user_id):
        """Endpoint should handle errors gracefully."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.create.side_effect = Exception("Database error")

            response = test_client.post(
                "/api/new/endpoint",
                json={"field": "value"},
                headers=auth_headers,
            )

        assert response.status_code == 500
```

## Review Checklist

When reviewing test PRs:

### Code Review
- [ ] Tests follow existing patterns
- [ ] Tests use shared fixtures
- [ ] Tests are properly mocked
- [ ] Tests have clear names
- [ ] Tests have docstrings

### Completeness
- [ ] All endpoints tested
- [ ] All status codes tested
- [ ] All error cases tested
- [ ] Edge cases covered
- [ ] Security cases covered

### Quality
- [ ] Tests are fast
- [ ] Tests are isolated
- [ ] Tests are maintainable
- [ ] Coverage is adequate
- [ ] Documentation updated

## Common Mistakes to Avoid

### ❌ Don't
- Don't make real API calls
- Don't access real database
- Don't make real LLM calls
- Don't test implementation details
- Don't create interdependent tests
- Don't hardcode sensitive data
- Don't skip error cases
- Don't ignore edge cases

### ✅ Do
- Mock all external dependencies
- Test behavior, not implementation
- Keep tests isolated
- Use descriptive test names
- Test all code paths
- Handle edge cases
- Document complex tests
- Follow existing patterns

## Debugging Checklist

When a test fails:
- [ ] Read the error message
- [ ] Check the traceback
- [ ] Run with `-vv` for verbose output
- [ ] Run with `-s` to see print statements
- [ ] Run with `--pdb` to debug
- [ ] Check mocking is correct
- [ ] Verify fixtures are set up
- [ ] Check for state leakage

## Quick Commands Reference

```bash
# Run all tests
pytest tests/integration/test_api_endpoints.py -v

# Run specific test
pytest tests/integration/test_api_endpoints.py::TestClass::test_method -v

# Run with coverage
pytest tests/integration/test_api_endpoints.py --cov=main --cov=api

# Debug failing test
pytest tests/integration/test_api_endpoints.py::FailingTest -vv --pdb

# Show print statements
pytest tests/integration/test_api_endpoints.py::TestClass -v -s
```

## Resources

- [README.md](./README.md) - Full documentation
- [QUICK_START.md](./QUICK_START.md) - Quick reference
- [SUMMARY.md](./SUMMARY.md) - What was created
- [../conftest.py](../conftest.py) - Shared fixtures
