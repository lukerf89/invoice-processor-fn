# Task Template for Invoice Processing

## Task [NN]: [Component Name] - [Specific Action]

**Status**: Pending
**Priority**: [High/Medium/Low]
**Estimated Duration**: [1-4 hours]
**Dependencies**: [List any dependencies]
**Engineering Principles Applied**: [List relevant principles 1-10]

## Description

[Brief description of what this task accomplishes]

## Context

- **Enables**: [What tasks this enables]
- **Integration Points**: [AI services, APIs, etc.]
- **Files to Create/Modify**:
  - `main.py` - [specific functions]
  - `test_scripts/test_[component].py` - [test files]

## TDD Implementation Cycle

### Phase 1: RED - Write Failing Tests

**Test Files to Create**:
- `test_scripts/test_[component].py` - Core logic tests
- Additional test files as needed

**Required Test Categories**:

#### Happy Path Tests
```python
def test_[component]_processes_[scenario]_successfully():
    # Arrange
    test_data = load_test_fixture('test_invoices/sample.pdf')
    expected_result = [expected_output]

    # Act
    result = [function_under_test](test_data)

    # Assert
    assert result == expected_result
    assert len(result) > 0
    assert all('required_field' in item for item in result)
```

#### Error Handling Tests
```python
def test_handles_[error_condition]_gracefully():
    # Test specific error scenarios
    pass
```

#### Edge Case Tests
```python
def test_handles_[edge_case]_correctly():
    # Test boundary conditions and edge cases
    pass
```

### Phase 2: GREEN - Minimal Implementation

**Implementation Structure**:
```python
def [function_name](input_data):
    """
    [Function description]

    Args:
        input_data: [Description]

    Returns:
        [Description]

    Raises:
        [Exception types and conditions]
    """
    # Minimal implementation to make tests pass
    pass
```

### Phase 3: REFACTOR - Improve Design

**Refactoring Focus**:
- [ ] Extract reusable utility functions
- [ ] Optimize performance
- [ ] Improve error handling
- [ ] Add comprehensive logging
- [ ] Enhance code documentation

## Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Test coverage ≥ 90% for business logic
- [ ] [Specific functionality criteria]
- [ ] Error handling tested for all failure modes
- [ ] Performance within acceptable bounds
- [ ] Logging includes structured data with correlation IDs
- [ ] Integration tests verify external dependencies
- [ ] Documentation updated

## Engineering Principles Compliance

**[Principle N]. [Name]**: [How this task applies the principle]

## Monitoring & Observability

**Required Metrics**:
- [Metric 1]: [Description]
- [Metric 2]: [Description]

**Log Events**:
```python
# Success case
logger.info("[Task] completed successfully", extra={
    'correlation_id': correlation_id,
    'processing_time_ms': elapsed,
    'items_processed': count
})

# Error case
logger.error("[Task] failed", extra={
    'correlation_id': correlation_id,
    'error_type': error.__class__.__name__,
    'error_message': str(error)
})
```

## Security Considerations

- [ ] [Security requirement 1]
- [ ] [Security requirement 2]

## Performance Requirements

- [ ] [Performance requirement 1]
- [ ] [Performance requirement 2]

## Implementation Notes

**Key Design Decisions**:
- [Decision 1 and rationale]
- [Decision 2 and rationale]

**Integration Points**:
- [Service/API integration details]

## Testing Strategy

**Test Coverage**:
- [ ] Unit tests for core logic
- [ ] Integration tests for external services
- [ ] Error scenario testing
- [ ] Performance testing
- [ ] Edge case validation
