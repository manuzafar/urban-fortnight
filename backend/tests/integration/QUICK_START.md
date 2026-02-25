# API Integration Tests - Quick Start Guide

## Quick Test Commands

### Run Everything
```bash
# All integration tests
pytest tests/integration/test_api_endpoints.py -v

# With coverage report
pytest tests/integration/test_api_endpoints.py --cov=main --cov=api --cov-report=html

# Fast mode (stop on first failure)
pytest tests/integration/test_api_endpoints.py -x
```

### Test Specific Features

#### V3 Discovery API
```bash
# All V3 tests
pytest tests/integration/test_api_endpoints.py -k "Discovery" -v

# Just session management
pytest tests/integration/test_api_endpoints.py::TestDiscoverySessionEndpoint -v

# Just start endpoint
pytest tests/integration/test_api_endpoints.py::TestDiscoveryStartEndpoint -v
```

#### V4 Discovery API
```bash
# All V4 test endpoints
pytest tests/integration/test_api_endpoints.py -k "V4Test" -v

# Session creation and retrieval
pytest tests/integration/test_api_endpoints.py::TestV4CreateTestSession -v
pytest tests/integration/test_api_endpoints.py::TestV4GetTestSession -v

# Stage execution
pytest tests/integration/test_api_endpoints.py::TestV4RunTestStage -v
pytest tests/integration/test_api_endpoints.py::TestV4StageExecutionWithMocking -v

# Interview management
pytest tests/integration/test_api_endpoints.py::TestV4AddInterview -v
pytest tests/integration/test_api_endpoints.py::TestV4InterviewManagement -v
```

#### Authentication Tests
```bash
# All auth-related tests
pytest tests/integration/test_api_endpoints.py -k "auth" -v

# V4 authenticated endpoints
pytest tests/integration/test_api_endpoints.py::TestV4AuthenticatedEndpoints -v
```

#### Export Tests
```bash
# All export tests
pytest tests/integration/test_api_endpoints.py -k "Export" -v

# Just PDF
pytest tests/integration/test_api_endpoints.py::TestExportPdfEndpoint -v

# Just DOCX
pytest tests/integration/test_api_endpoints.py::TestExportDocxEndpoint -v
```

#### Security & Validation
```bash
# Input sanitization
pytest tests/integration/test_api_endpoints.py::TestInputSanitization -v

# Error handling
pytest tests/integration/test_api_endpoints.py::TestErrorHandling -v

# Schema validation
pytest tests/integration/test_api_endpoints.py::TestResponseSchemaValidation -v
```

#### SSE Streaming
```bash
pytest tests/integration/test_api_endpoints.py::TestSSEStreamingEndpoint -v
```

### Test by Status Code

```bash
# All 404 tests
pytest tests/integration/test_api_endpoints.py -k "404" -v

# All auth failures (401/403)
pytest tests/integration/test_api_endpoints.py -k "requires_auth" -v

# All validation failures (422)
pytest tests/integration/test_api_endpoints.py -k "invalid" -v
```

## Common Scenarios

### Scenario 1: Testing New V4 Stage
```bash
# Test all stage execution
pytest tests/integration/test_api_endpoints.py::TestV4StageExecutionWithMocking::test_run_all_valid_stages -v

# Test specific stage
pytest tests/integration/test_api_endpoints.py::TestV4RunTestStage::test_run_stage_valid_request -v
```

### Scenario 2: Testing Database Persistence
```bash
pytest tests/integration/test_api_endpoints.py::TestV4DatabasePersistence -v
```

### Scenario 3: Testing Error Handling
```bash
# Stage errors
pytest tests/integration/test_api_endpoints.py::TestV4StageExecutionWithMocking::test_stage_error_handling -v

# General errors
pytest tests/integration/test_api_endpoints.py::TestErrorHandling -v
```

### Scenario 4: Testing Lifecycle Flow
```bash
# V4 continuation to full lifecycle
pytest tests/integration/test_api_endpoints.py::TestV4LifecycleContinuation -v
```

## Debugging Failed Tests

### 1. Show full error output
```bash
pytest tests/integration/test_api_endpoints.py::FailingTest -vv --tb=long
```

### 2. Drop into debugger on failure
```bash
pytest tests/integration/test_api_endpoints.py::FailingTest --pdb
```

### 3. Show print statements
```bash
pytest tests/integration/test_api_endpoints.py::FailingTest -s
```

### 4. Run with logging
```bash
pytest tests/integration/test_api_endpoints.py::FailingTest -v --log-cli-level=DEBUG
```

## Performance Testing

### Run tests with timing
```bash
pytest tests/integration/test_api_endpoints.py --durations=10
```

### Run in parallel (requires pytest-xdist)
```bash
pytest tests/integration/test_api_endpoints.py -n auto
```

## CI/CD Commands

### Pre-commit checks
```bash
# Run all integration tests
pytest tests/integration/test_api_endpoints.py -v --tb=short

# With coverage threshold
pytest tests/integration/test_api_endpoints.py --cov=main --cov=api --cov-report=term --cov-fail-under=85
```

### GitHub Actions format
```bash
pytest tests/integration/test_api_endpoints.py -v --junitxml=test-results.xml
```

## Test Development Workflow

### 1. Run single test while developing
```bash
pytest tests/integration/test_api_endpoints.py::TestClass::test_method -v -s
```

### 2. Run test class
```bash
pytest tests/integration/test_api_endpoints.py::TestClass -v
```

### 3. Run all tests
```bash
pytest tests/integration/test_api_endpoints.py -v
```

### 4. Update and validate
```bash
# Watch mode (requires pytest-watch)
ptw tests/integration/test_api_endpoints.py
```

## Common Flags

| Flag | Purpose |
|------|---------|
| `-v` | Verbose output |
| `-vv` | Very verbose output |
| `-s` | Show print statements |
| `-x` | Stop on first failure |
| `-k "pattern"` | Run tests matching pattern |
| `--tb=short` | Short traceback |
| `--tb=long` | Full traceback |
| `--pdb` | Drop into debugger on failure |
| `--durations=N` | Show N slowest tests |
| `--cov=module` | Coverage for module |
| `--cov-report=html` | HTML coverage report |
| `-n auto` | Parallel execution |

## Expected Test Times

- Individual test: <0.1s
- Test class: <1s
- Full suite: <30s
- With coverage: <45s

## Test Count Summary

- Health: 2 tests
- V3 Discovery: 24 tests
- Export: 8 tests
- V4 Test Endpoints: 34 tests
- V4 Authenticated: 4 tests
- SSE Streaming: 4 tests
- V4 Advanced: 15 tests
- Validation: 3 tests
- Error Handling: 3 tests
- Security: 3 tests
- Edge Cases: 5 tests

**Total: 105+ tests**

## Troubleshooting

### Issue: Import errors
```bash
# Ensure you're in the backend directory
cd /path/to/backend

# Check Python path
python -c "import sys; print(sys.path)"
```

### Issue: Module not found
```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Issue: Tests hang
```bash
# Check for async issues, run with timeout
pytest tests/integration/test_api_endpoints.py --timeout=10
```

### Issue: Flaky tests
```bash
# Run multiple times to identify
pytest tests/integration/test_api_endpoints.py::FlakyTest --count=10
```

## Pro Tips

1. **Use test markers**: Add custom markers for easier filtering
2. **Keep tests fast**: Mock external calls (DB, LLM, HTTP)
3. **Test isolation**: Each test should be independent
4. **Clear names**: Test name should describe what it tests
5. **One assert focus**: Each test should verify one behavior

## Next Steps

- Review [README.md](./README.md) for detailed documentation
- Check [../conftest.py](../conftest.py) for shared fixtures
- See [../../main.py](../../main.py) for API implementation
- Review [../../api/discovery_v4_routes.py](../../api/discovery_v4_routes.py) for V4 routes
