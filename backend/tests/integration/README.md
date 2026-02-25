# API Integration Tests

Comprehensive integration tests for all backend API endpoints.

## Overview

This test suite covers:
- **V3 Discovery endpoints** (main.py)
- **V4 Discovery endpoints** (api/discovery_v4_routes.py)
- **Export endpoints** (PDF/DOCX)
- **SSE streaming**
- **Database persistence**
- **Authentication and authorization**

## Test Structure

```
test_api_endpoints.py
├── Health Check Tests
│   └── TestHealthEndpoint
├── V3 Discovery Tests
│   ├── TestDiscoveryStartEndpoint
│   ├── TestDiscoverySessionEndpoint
│   ├── TestListSessionsEndpoint
│   ├── TestDeleteSessionEndpoint
│   └── TestGetPackEndpoint
├── Export Tests
│   ├── TestExportPdfEndpoint
│   └── TestExportDocxEndpoint
├── V4 Discovery Tests
│   ├── TestV4CreateTestSession
│   ├── TestV4GetTestSession
│   ├── TestV4RunTestStage
│   ├── TestV4ApproveStage
│   ├── TestV4SkipStage
│   ├── TestV4SaveStageOutput
│   ├── TestV4AddInterview
│   └── TestV4SynthesizeInterviews
├── V4 Authenticated Endpoint Tests
│   └── TestV4AuthenticatedEndpoints
├── SSE Streaming Tests
│   └── TestSSEStreamingEndpoint
├── V4 Advanced Tests
│   ├── TestV4StageExecutionWithMocking
│   ├── TestV4DatabasePersistence
│   ├── TestV4InterviewManagement
│   └── TestV4LifecycleContinuation
├── Validation Tests
│   └── TestResponseSchemaValidation
├── Error Handling Tests
│   └── TestErrorHandling
├── Security Tests
│   └── TestInputSanitization
└── Edge Cases
    └── TestEdgeCasesAndBoundaries
```

## Running Tests

### Run all integration tests
```bash
pytest tests/integration/test_api_endpoints.py -v
```

### Run specific test class
```bash
pytest tests/integration/test_api_endpoints.py::TestV4CreateTestSession -v
```

### Run specific test
```bash
pytest tests/integration/test_api_endpoints.py::TestHealthEndpoint::test_health_returns_200 -v
```

### Run with coverage
```bash
pytest tests/integration/test_api_endpoints.py --cov=main --cov=api --cov-report=term
```

### Use the test runner script
```bash
chmod +x run_api_tests.sh
./run_api_tests.sh                          # Run all tests
./run_api_tests.sh TestV4RunTestStage       # Run specific class
```

## Test Categories

### 1. Health Check Tests (2 tests)
- `test_health_returns_200` - Basic health check returns 200
- `test_health_returns_status` - Health check includes status info

### 2. V3 Discovery Endpoints (24 tests)
#### Start Endpoint
- Authentication required
- Valid request acceptance
- Product idea validation (min length, required field)
- Max concurrent sessions handling
- Optional fields handling

#### Session Status
- Authentication required
- 404 for non-existent sessions
- 404 for unauthorized access
- Successful status retrieval
- Inception pack inclusion for completed sessions

#### Session Management
- List sessions (empty, with data)
- Delete sessions
- Get inception pack

### 3. Export Endpoints (8 tests)
- PDF export (auth, 404, invalid section, not completed)
- DOCX export (auth, 404, invalid section)

### 4. V4 Discovery Test Endpoints (34 tests)
#### Session Creation
- Success without auth (test endpoint)
- Product idea validation
- Default mode (guided)

#### Session Retrieval
- 404 for non-existent
- From cache
- From database

#### Stage Execution
- 404 for missing session
- Invalid stage names
- Valid stage requests
- All 5 stages (problem_love, customer_truth, opportunity_mapping, solution_design, validation_plan)
- Stage state updates (in_progress, completed)
- Error handling

#### Stage Actions
- Approve stage
- Skip stage
- Save output

#### Interview Management
- Add interviews
- Multiple interviews
- Synthesize patterns
- Evidence quality updates

### 5. V4 Authenticated Endpoints (4 tests)
- Create session requires auth
- Get session requires auth
- Run stage requires auth
- List sessions requires auth

### 6. SSE Streaming Tests (4 tests)
- Token required
- Invalid token rejection
- 404 for missing session
- Done event for completed sessions

### 7. V4 Advanced Tests (15 tests)
#### Stage Execution with Mocking
- Session state updates
- All valid stages execution
- Database persistence
- Error handling

#### Database Persistence
- Load from DB when not cached
- Create persists to DB
- Stage output save persists

#### Interview Management
- Multiple interviews
- Evidence quality updates
- Synthesis requirements

#### Lifecycle Continuation
- Requires completed stages
- Background task queueing

### 8. Validation Tests (3 tests)
- DiscoveryResponse schema
- SessionStatusResponse schema
- DiscoverySessionV4 schema

### 9. Error Handling Tests (3 tests)
- Invalid JSON returns 422
- Wrong content type returns 422
- Malformed session IDs handled gracefully

### 10. Security Tests (3 tests)
- XSS payload handling
- SQL injection prevention
- Very long input rejection

### 11. Edge Cases (5 tests)
- Concurrent stage runs
- Special characters in product ideas
- Empty stage outputs
- Session ID format variations

## Total: 105+ Tests

## Fixtures

### Authentication Fixtures
- `valid_jwt_token` - Mock JWT token
- `test_user_id` - Test user UUID
- `auth_headers` - Headers with Bearer token

### Request Fixtures
- `sample_discovery_request` - Valid V3 discovery request
- `sample_v4_session_request` - Valid V4 session request
- `sample_interview_data` - Valid interview data

### Session Fixtures
- `sample_session_data` - Pending session
- `sample_completed_session` - Completed session
- `sample_inception_pack` - Sample pack data

## Mocking Strategy

### Database Mocking
```python
with patch("main.session_store") as mock_store:
    mock_store.get.return_value = session_data
    mock_store.create.return_value = None
```

### Authentication Mocking
```python
with patch("utils.auth.decode_supabase_jwt") as mock_decode:
    mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
```

### LLM Mocking
```python
with patch("agents.discovery_v4.engine.DiscoveryEngineV4.run_stage") as mock_run:
    mock_run.side_effect = Exception("LLM API error")
```

### In-Memory Session Cache
```python
with patch("api.discovery_v4_routes._active_sessions", {"session-id": mock_session}):
    # Test code
```

## Key Testing Patterns

### 1. Authentication Testing
All authenticated endpoints test:
- Missing auth (401/403)
- Invalid auth (401/403)
- Valid auth (200)
- Ownership verification

### 2. Validation Testing
All input endpoints test:
- Missing required fields (422)
- Invalid field values (422)
- Valid inputs (200/202)

### 3. Database Persistence
V4 endpoints test:
- Cache-first lookups
- Database fallback
- Persistence after mutations

### 4. Error Handling
All endpoints test:
- Graceful degradation
- Proper status codes
- Error messages

## Coverage Goals

- **Line Coverage**: >85%
- **Branch Coverage**: >80%
- **Endpoint Coverage**: 100%

## CI/CD Integration

These tests run:
- On every PR
- On merge to main
- Nightly full suite

## Common Issues

### 1. Import Errors
**Solution**: Ensure backend directory is in `sys.path`
```python
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
```

### 2. Async Test Failures
**Solution**: Use proper async mocking
```python
mock_func = AsyncMock(return_value=result)
```

### 3. Session Store Conflicts
**Solution**: Mock both stores
```python
with patch("main.session_store") as mock_main_store, \
     patch("api.discovery_v4_routes.session_store") as mock_v4_store:
```

## Best Practices

1. **Isolation**: Each test is independent
2. **Mocking**: Mock external dependencies (DB, LLM, auth)
3. **Fixtures**: Reuse common data
4. **Assertions**: Test behavior, not implementation
5. **Documentation**: Clear test names and docstrings

## Adding New Tests

### Template for New Endpoint Test
```python
class TestNewEndpoint:
    """Tests for /api/new/endpoint."""

    def test_requires_auth(self, test_client):
        """Endpoint should require authentication."""
        response = test_client.get("/api/new/endpoint")
        assert response.status_code in [401, 403]

    def test_success_case(self, test_client, auth_headers, test_user_id):
        """Endpoint should return expected data."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.method.return_value = expected_data

            response = test_client.get(
                "/api/new/endpoint",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data

    def test_error_case(self, test_client, auth_headers, test_user_id):
        """Endpoint should handle errors gracefully."""
        # Test implementation
```

## Maintenance

- Update tests when endpoints change
- Add tests for new endpoints
- Review coverage reports monthly
- Update fixtures when schemas change

## Related Documentation

- [Backend README](/Users/manuzafarabdulla/Fun Projects/Product LifeCycle/backend/README.md)
- [API Documentation](/Users/manuzafarabdulla/Fun Projects/Product LifeCycle/docs/API.md)
- [Testing Strategy](/Users/manuzafarabdulla/Fun Projects/Product LifeCycle/docs/TESTING.md)
