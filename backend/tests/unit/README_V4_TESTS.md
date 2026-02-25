# Discovery V4 Test Suite

This document describes the test coverage for the Discovery V4 system.

## Test Files

### 1. `test_discovery_v4_engine.py`
Tests for the Discovery Engine V4 orchestrator that coordinates the 5-stage discovery process.

**Coverage:**
- ✅ Mode configuration (Quick, Guided, Deep)
- ✅ Stage runner lazy loading
- ✅ Stage execution and status transitions
- ✅ Error handling during stage execution
- ✅ Context building from previous stages
- ✅ Quality gates and blocking conditions
- ✅ Evidence tier calculation based on interviews
- ✅ Session progress tracking
- ✅ Cross-stage data updates (patterns, four_forces, opportunity_tree)
- ✅ Mode-specific requirements (e.g., Deep mode interview requirements)

**Test Count:** 17 tests
**Status:** All passing ✅

### 2. `test_discovery_v4_stages.py` (WIP)
Tests for individual stage implementations.

**Intended Coverage:**
- Problem Love Stage (Stage 1)
  - LLM-based problem analysis
  - Frequency normalization
  - Reflection loop iterations
  - Tarpit detection
  - Error handling

- Customer Truth Stage (Stage 2)
  - Interview synthesis
  - Pattern extraction
  - Hypothetical generation for Quick mode
  - Deep mode interview requirements
  - Interview guide generation

- Opportunity Mapping Stage (Stage 3)
  - 4 Forces Model analysis
  - Opportunity Solution Tree generation
  - Evidence-based opportunity prioritization

- Solution Design Stage (Stage 4)
  - DHM score calculation
  - Pre-mortem analysis
  - Solution concept generation

- Validation Plan Stage (Stage 5)
  - Validation ladder creation
  - Experiment planning
  - Status normalization

**Status:** Needs LLM mocking fixes ⚠️

## Running the Tests

### Run all V4 tests:
```bash
cd backend
./venv/bin/python -m pytest tests/unit/test_discovery_v4*.py -v
```

### Run engine tests only:
```bash
./venv/bin/python -m pytest tests/unit/test_discovery_v4_engine.py -v
```

### Run with coverage:
```bash
./venv/bin/python -m pytest tests/unit/test_discovery_v4*.py --cov=agents.discovery_v4 --cov-report=term
```

## Test Patterns

### Mocking LLM Calls
The tests properly mock LLM calls at the module level to avoid making real API calls:

```python
with patch("agents.discovery_v4.stages.problem_love.call_llm", return_value=mock_response):
    output = await stage.run(session, context)
```

### Mocking Database Calls
Database persistence is mocked to avoid requiring a live Supabase connection:

```python
with patch("agents.discovery_v4.engine.session_store") as mock_store:
    mock_store.update_status = MagicMock()
    # test code
```

### Mocking Stage Runners
Since `stage_runners` is a property with lazy loading, tests directly set the private attribute:

```python
engine._stage_runners = {"problem_love": mock_runner}
```

## Key Test Scenarios

### 1. State Transitions
Tests verify that stages transition through the correct states:
- `NOT_STARTED` → `IN_PROGRESS` → `COMPLETED`
- Error handling returns to `NOT_STARTED` with error message

### 2. Quality Gates
Tests verify quality gate enforcement:
- Minimum score thresholds
- Required field validation
- Mode-specific requirements (e.g., Deep mode needs 3+ interviews)

### 3. Evidence Tiers
Tests verify evidence tier calculation based on interview count:
- 0 interviews → E4 (AI-generated)
- 1-2 interviews → E3 (Partial evidence)
- 3-4 interviews → E2 (Verified patterns)
- 5+ interviews → E1 (Direct customer quotes)

### 4. Progress Tracking
Tests verify session progress calculation:
- Progress percentage (completed stages / total stages)
- Overall quality score (average of stage scores)
- Status updates (in_progress → completed)

### 5. Cross-Stage Data Flow
Tests verify data flows between stages:
- Problem statement from Problem Love → Customer Truth
- Patterns from Customer Truth → Opportunity Mapping
- Four Forces & Opportunity Tree → Solution Design
- DHM score → Validation Plan

## Schema Validation

All tests use the Pydantic schemas from `models.discovery_v4_schemas.py` to ensure:
- Output structure matches expected format
- Required fields are present
- Enum values are valid
- Data types are correct

## Error Handling

Tests verify graceful error handling:
- LLM API failures
- Invalid stage names
- Missing required context
- Database persistence failures (non-blocking)

## Future Test Coverage

### Additional scenarios to test:
1. **Reflection Loop Edge Cases**
   - Max iterations reached
   - Oscillating scores
   - Consistent low scores

2. **Mode-Specific Flows**
   - Quick mode auto-run all stages
   - Guided mode checkpoints
   - Deep mode interview-driven flow

3. **Coaching & Assistance**
   - AI coaching message generation
   - Pattern synthesis suggestions
   - Validation experiment recommendations

4. **Export & Persistence**
   - Draft state saving
   - Session resumption
   - Interview data persistence

## Integration Tests

The V4 system also needs integration tests for:
- End-to-end session execution
- API endpoint testing (see `api/discovery_v4_routes.py`)
- SSE streaming for real-time updates
- Database persistence and retrieval

## Performance Tests

Consider adding performance tests for:
- Stage execution time limits
- Reflection loop convergence speed
- Quality gate evaluation performance
- Memory usage with many interviews

## References

- Main implementation: `backend/agents/discovery_v4/`
- Schemas: `backend/models/discovery_v4_schemas.py`
- API routes: `backend/api/discovery_v4_routes.py`
- Documentation: `CLAUDE.md` (V4 Discovery System section)
