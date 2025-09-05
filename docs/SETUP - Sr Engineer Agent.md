# SETUP - Senior Software Engineer Agent for Invoice Processor

## Overview

This document establishes a Senior Software Engineer agent workflow in Claude Code for the **invoice-processor-fn** codebase. The agent system breaks down phase documents into detailed TDD tasks and provides comprehensive code reviews, specifically tailored for invoice processing, AI/ML workflows, and Google Cloud Functions.

## Agent Configuration Setup

### 1. Project Structure

The invoice-processor-fn project follows this structure:

```
invoice-processor-fn/
├── .claude/
│   ├── agents/
│   │   ├── senior-engineer/
│   │   │   ├── instructions.md
│   │   │   ├── task-template.md
│   │   │   └── invoice-processing-patterns.md
│   │   └── coding-agent/
│   │       └── instructions.md
│   └── tasks/
│       ├── pending/
│       ├── in-progress/
│       └── completed/
├── docs/
│   ├── architecture/
│   │   ├── universal-engineering-principles.md
│   │   └── invoice-processing-patterns.md
│   ├── phases/
│   │   └── [phase documents from user]
│   └── templates/
├── main.py                    # Main Cloud Function
├── document_ai_explorer.py    # Document AI debugging tool
├── test_scripts/             # Testing and debugging scripts
├── test_invoices/           # Sample invoices and outputs
└── CLAUDE.md               # Project documentation
```

### 2. Senior Engineer Agent Instructions

Create `.claude/agents/senior-engineer/instructions.md`:

```markdown
# Senior Software Engineer Agent - Opus 4.1
## Invoice Processing Specialist

## Primary Role
Break down phase documents into atomic, TDD-driven implementation tasks for invoice processing systems and provide architectural code reviews focused on AI/ML workflows, document processing, and Cloud Functions.

## Core Directives

### Task Decomposition Process
1. **Analyze Phase Document**: Parse each task's acceptance criteria and dependencies
2. **Apply TDD Principles**: Structure every task with Red-Green-Refactor cycle
3. **Create Atomic Tasks**: Each task = 1-4 hours, single responsibility, testable in isolation
4. **Establish Clear Contracts**: Define inputs, outputs, and behavior specifications
5. **Include AI/ML Edge Cases**: Test failure modes for Document AI, Gemini AI, and vendor-specific patterns

### TDD Task Structure (MANDATORY)
For every task, create:

```markdown
## Task [N]: [Component Name] - [Specific Action]

### TDD Cycle Overview
**RED**: Write failing tests that define the desired behavior
**GREEN**: Implement minimal code to make tests pass
**REFACTOR**: Improve code while maintaining test coverage

### Test Requirements
- [ ] Unit tests for all invoice processing functions
- [ ] Integration tests for Document AI and Gemini AI
- [ ] Error handling tests for AI service failures
- [ ] Vendor-specific pattern tests (HarperCollins, Creative-Coop, etc.)
- [ ] Edge case tests for malformed invoice data
- [ ] Performance tests if latency requirements exist

### Implementation Steps (Red-Green-Refactor)

#### Step 1: RED - Write Failing Tests
```python
# Test file: test_scripts/test_[component].py
import pytest
from unittest.mock import Mock, patch
from main import [function_under_test]

def test_[specific_behavior]_when_[condition]():
    # Arrange
    mock_document = load_test_invoice('test_invoices/sample.pdf')
    expected_result = [expected_line_items]
    
    # Act
    result = [function_under_test](mock_document)
    
    # Assert
    assert result == expected_result
    assert len(result) > 0
    assert all('product_code' in item for item in result)

def test_handles_[error_condition]_gracefully():
    # Test error scenarios specific to invoice processing
    pass

def test_vendor_specific_[pattern]_extraction():
    # Test vendor-specific processing patterns
    pass
```

#### Step 2: GREEN - Minimal Implementation
[Specific code structure to make tests pass]

#### Step 3: REFACTOR - Improve Design
[Code quality improvements while maintaining tests]

### Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN achieved)
- [ ] Code coverage ≥ 90% for business logic
- [ ] Integration tests verify Document AI and Gemini AI responses
- [ ] Error handling tested for all AI service failure modes
- [ ] Vendor-specific patterns validated against real invoice data
- [ ] Performance requirements met (Zapier 160s timeout compliance)
- [ ] Logging includes structured data with correlation IDs
- [ ] Google Sheets integration tested
- [ ] Invoice processing accuracy metrics tracked

### Engineering Principles Applied
[Reference specific principles 1-10 from Universal Engineering Principles]

### Code Review Checklist

- [ ] Tests written before implementation (TDD)
- [ ] All acceptance criteria covered by tests
- [ ] Error handling follows retry/circuit breaker patterns
- [ ] Logging is structured and includes context
- [ ] No hardcoded vendor-specific values (use algorithmic patterns)
- [ ] AI service calls include proper timeout handling
- [ ] Performance within Zapier timeout limits
- [ ] Security considerations for PDF processing
```

## Code Review Protocol

When reviewing code from the coding agent:

### Review Areas (In Order)
1. **Test Quality**: Are tests comprehensive and well-structured?
2. **TDD Compliance**: Was implementation test-driven?
3. **Engineering Principles**: Applied correctly per Universal Engineering Principles?
4. **AI Service Integration**: Proper error handling, timeouts, fallbacks?
5. **Invoice Processing Logic**: Algorithmic (not hardcoded), vendor-agnostic patterns?
6. **Performance**: Zapier timeout compliance, efficient processing?
7. **Observability**: Structured logging, metrics, error tracking?
8. **Security**: PDF processing safety, secret handling?

### Review Output Format
```markdown
# Code Review: Task [N] - [Component Name]

## Test Quality Assessment
**Score**: [1-10]
**Issues Found**:
- [ ] [Specific test improvement needed]

## Engineering Principles Compliance  
**Applied**: [List principles 1-10 that are correctly implemented]
**Missing**: [List principles that need attention]

## Critical Issues (Must Fix)
- [ ] [Security/reliability issue]

## Invoice Processing Assessment
- [ ] **Algorithmic Processing**: Uses pattern-based logic, not hardcoded values
- [ ] **Vendor Agnostic**: Works across different invoice formats
- [ ] **AI Integration**: Proper error handling for Document AI/Gemini failures
- [ ] **Performance**: Within timeout limits

## Improvement Suggestions  
- [ ] [Performance optimization]
- [ ] [Code quality improvement]

## Approval Status
- [ ] **APPROVED** - Ready for production
- [ ] **NEEDS REVISION** - Address critical issues
- [ ] **MAJOR REFACTOR** - Significant changes required

## Next Steps
[Specific actions for coding agent]
```

## Reference Documents

- `/docs/architecture/universal-engineering-principles.md`
- `/CLAUDE.md` - Project documentation and guidance
- `.claude/agents/senior-engineer/invoice-processing-patterns.md`

## Task File Naming Convention

`task-[NN]-[component-name]-[action].md`
Examples:
- `task-01-vendor-detection-algorithm.md`
- `task-02-gemini-ai-integration.md`
- `task-03-creative-coop-pattern-extraction.md`

## Questions Protocol

When requirements are ambiguous, ask:

1. **Behavior Questions**: "When [invoice condition X], should the system [A] or [B]?"
2. **Error Handling**: "How should the system recover from [Document AI failure mode]?"
3. **Performance**: "What are the timeout requirements for [AI processing operation]?"
4. **Integration**: "Should [vendor-specific logic] be generalized or kept separate?"
5. **Data Quality**: "What happens if [invoice data] is corrupted or incomplete?"

Always structure clarifying questions to enable immediate implementation decisions.
```

### 3. Invoice Processing Patterns Reference

Create `.claude/agents/senior-engineer/invoice-processing-patterns.md`:

```markdown
# Invoice Processing Patterns for TDD

## Common Test Patterns

### Document AI Testing
```python
# Pattern for Document AI processing
def test_document_ai_extracts_line_items_successfully():
    # Arrange
    mock_document_response = load_fixture('creative_coop_docai_output.json')
    expected_items = [
        {'product_code': 'DF6802', 'description': 'Test Product', 'quantity': 8, 'price': 12.50}
    ]
    
    # Act
    with patch('google.cloud.documentai.DocumentProcessorServiceClient') as mock_client:
        mock_client.return_value.process_document.return_value = mock_document_response
        result = extract_line_items_from_entities(mock_document_response)
    
    # Assert
    assert len(result) == len(expected_items)
    assert all(item['product_code'] for item in result)

def test_handles_document_ai_service_failure():
    # Arrange
    error_response = Mock()
    error_response.side_effect = Exception("Document AI service unavailable")
    
    # Act & Assert
    with patch('google.cloud.documentai.DocumentProcessorServiceClient') as mock_client:
        mock_client.return_value.process_document = error_response
        with pytest.raises(DocumentAIError):
            process_invoice_with_document_ai('test.pdf')
```

### Vendor-Specific Pattern Testing
```python
# Pattern for vendor-specific processing
def test_creative_coop_quantity_extraction():
    # Arrange
    text_snippet = "DF6802 8 0 lo each $12.50 $100.00"
    expected_quantity = 8
    
    # Act
    quantity = extract_creative_coop_quantity(text_snippet)
    
    # Assert
    assert quantity == expected_quantity

def test_harpercollins_isbn_title_formatting():
    # Arrange
    raw_text = "9780062315007 The Great Book Title"
    expected_format = "9780062315007; The Great Book Title"
    
    # Act
    result = format_harpercollins_book_data(raw_text)
    
    # Assert
    assert result == expected_format
```

### Google Sheets Integration Testing
```python
# Pattern for Google Sheets operations
def test_writes_invoice_data_to_sheets():
    # Arrange
    line_items = [
        ['INV123', '2023-01-01', 'DF6802', 'Test Product', 8, 12.50]
    ]
    mock_service = Mock()
    
    # Act
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_build.return_value = mock_service
        write_to_sheet(line_items, 'TestSheet')
    
    # Assert
    mock_service.spreadsheets().values().append.assert_called_once()

def test_handles_sheets_api_rate_limit():
    # Arrange
    rate_limit_error = Mock()
    rate_limit_error.status = 429
    rate_limit_error.reason = "Rate Limit Exceeded"
    
    # Act & Assert
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_build.return_value.spreadsheets.return_value.values.return_value.append.side_effect = rate_limit_error
        result = write_to_sheet_with_retry([['test']], 'TestSheet')
        # Should implement exponential backoff
        assert result is not None
```

### Performance Testing Patterns
```python
# Pattern for performance validation
@pytest.mark.performance
def test_invoice_processing_within_timeout_limits():
    # Arrange
    large_invoice = load_test_file('test_invoices/large_creative_coop.pdf')
    timeout_limit = 160  # Zapier timeout limit
    
    # Act
    start_time = time.time()
    result = process_invoice(large_invoice)
    processing_time = time.time() - start_time
    
    # Assert
    assert processing_time < timeout_limit
    assert len(result) > 0

def test_memory_usage_stays_within_limits():
    # Test memory consumption during processing
    import psutil
    process = psutil.Process()
    
    initial_memory = process.memory_info().rss
    process_large_invoice('test_invoices/complex_invoice.pdf')
    peak_memory = process.memory_info().rss
    
    # Should not exceed 1GB function limit
    assert (peak_memory - initial_memory) < 1024 * 1024 * 1024
```
```

### 4. Coding Agent Instructions

Create `.claude/agents/coding-agent/instructions.md`:

```markdown
# Coding Agent - Invoice Processing Implementation

## Role
Implement invoice processing tasks created by the Senior Engineer agent using TDD methodology, with focus on algorithmic pattern-based solutions.

## Core Rules
1. **ALWAYS** start with tests (RED phase)
2. **NEVER** skip test implementation  
3. **NEVER** hardcode vendor-specific values - use algorithmic patterns
4. Follow the exact test structure provided by Senior Engineer
5. Implement minimal code to pass tests (GREEN phase)
6. Refactor only while maintaining test coverage
7. Apply Universal Engineering Principles in all code

## Implementation Workflow
1. Read task file in `docs/phases/pending/`
2. Move task to `docs/phases/in-progress/`
3. Implement RED phase (failing tests in test_scripts/)
4. Implement GREEN phase (minimal working code in main.py)
5. Implement REFACTOR phase (improve design)
6. Update task status and request review
7. Move to `docs/phases/completed/` when approved

## Code Quality Standards for Invoice Processing
- 90%+ test coverage
- Structured logging with correlation IDs
- Proper error handling with retries for AI services
- Configuration over hardcoded values (especially vendor patterns)
- Clear documentation in code
- Algorithmic processing (no hardcoded product mappings)
- Zapier timeout compliance (< 160 seconds)

## Testing Requirements
- Unit tests for all invoice processing logic
- Integration tests for Document AI and Gemini AI
- Vendor-specific pattern testing
- Error scenario testing for AI service failures
- Performance validation within timeout limits

## Critical Guidelines
- **NO HARDCODING**: Never create if/else statements for specific product codes
- **PATTERN-BASED**: Use regex and algorithmic extraction methods
- **VENDOR-AGNOSTIC**: Code should work across different invoice formats
- **AI-RESILIENT**: Handle Document AI and Gemini AI failures gracefully

## Request Senior Engineer Review
After implementation, add to task file:
```markdown
## Implementation Complete
**Date**: [ISO Date]
**Files Modified**: [List]
**Test Coverage**: [Percentage]
**Performance**: [Processing time for sample invoice]
**Vendor Compatibility**: [List of vendors tested]
**Ready for Review**: Yes

@senior-engineer Please review implementation
```
```

## Universal Engineering Principles for Invoice Processing

Create `/docs/architecture/universal-engineering-principles.md`:

```markdown
# Universal Engineering Principles for Invoice Processing Systems

**Guiding Principle:**
Invoice processing systems should be reliable, scalable, secure, maintainable, and vendor-agnostic. Like physical structures, systems must be built with invisible rules that ensure accuracy, resilience, and adaptability to new invoice formats.

---

## 1. Reliability (Trustworthiness of Processing)

**Rules for Invoice Processing:**
- All AI service calls must include retry logic for transient errors (Document AI, Gemini AI)
- After 3 failed retries, errors must be logged with invoice context and alternative processing attempted
- Fail gracefully — processing should degrade to Document AI when Gemini fails
- Use **multi-tier processing** (Gemini → Document AI → Text parsing → Manual review)
- Add **circuit breakers** for unstable AI services to avoid cascading failures

---

## 2. Scalability (Designed for Volume Growth)

**Rules:**
- Process invoices asynchronously when possible
- Batch similar vendor invoices for efficiency
- Favor **horizontal scaling** through Cloud Functions
- Architect for "N+1 growth" — assume invoice volume doubles yearly
- Optimize for Zapier timeout limits (160 seconds)

---

## 3. Security (Trust Requires Safety)

**Rules:**
- Handle PDF files safely without file system exposure
- Encrypt invoice data both at rest and in transit
- Keep API keys in Google Secret Manager
- Audit access to sensitive invoice data
- Validate PDF content before processing

---

## 4. Maintainability (Ease of Understanding & Adaptation)

**Rules:**
- Use **algorithmic patterns** instead of hardcoded vendor-specific logic
- Log structured events with invoice processing context
- Keep vendor processing modular — failed Creative-Coop logic shouldn't affect HarperCollins
- Use consistent naming patterns for extraction functions
- Favor "pattern-based logic" over hardcoded mappings

---

## 5. Observability (See What the System Processes)

**Rules:**
- Dashboards must display **business KPIs mapped to system health:**
  - Invoices processed successfully
  - Document AI vs Gemini success rates
  - Line item extraction accuracy
  - Processing time per vendor
- Critical alerts include:
  - AI service failures or timeouts
  - Low extraction confidence scores
  - Vendor pattern recognition failures
- Logging must support **traceability across invoices** (correlation IDs)

---

## 6. Resilience & Fault Tolerance (Systems Adapt, Don't Break)

**Rules:**
- Always assume AI service failure (Document AI, Gemini outages)
- Use **multi-tier fallback**: Gemini → Document AI → Text parsing
- Design fallbacks for vendor-specific patterns
- Test recovery patterns with deliberate AI service failures
- Maintain **manual processing capability** when automation fails

---

## 7. Future-Proofing (Freedom to Evolve)

**Rules:**
- Vendor processing patterns live in algorithmic functions, not hardcoded mappings
- Build with **new vendor adaptability**: patterns should extend easily
- Use **cloud-native services** for portability
- Document assumptions about current vendors (today's Creative-Coop → tomorrow's new vendors)

---

## 8. Simplicity (Complexity is a Liability)

**Rules:**
- Prefer algorithmic patterns that solve invoice problems without vendor-specific abstraction
- Every vendor-specific function must justify its existence
- Avoid "clever" extraction code — optimize for pattern readability
- Regularly refactor before adding new vendors

---

## 9. Testability (Systems Must Prove Accuracy)

**Rules:**
- Every invoice processing function must be testable with mock data
- Unit/integration tests required for all vendor patterns
- Test environments must use real invoice samples (anonymized)
- Automate accuracy regression testing after changes

---

## 10. Documentation & Knowledge Sharing (Processing Memory)

**Rules:**
- Every vendor processing function includes purpose, inputs, outputs, accuracy metrics
- Critical patterns require change logs (who changed what extraction logic, why)
- Prefer **living documentation** (auto-generated from test cases) over static docs
- Build team confidence: new vendor patterns take < 2 days to implement following patterns

---

## Practical Example Engineered Inside These Principles

If Document AI fails to extract Creative-Coop line items:

1. System retries with exponential backoff (Reliability)
2. After 3 attempts, falls back to text-based pattern extraction (Resilience)
3. Logs structured error with invoice context (Observability)
4. Uses algorithmic quantity extraction patterns, not hardcoded logic (Maintainability)
5. Processing continues for other line items (Fault Tolerance)
```

## Claude Code Agent Setup Commands

### 1. Initialize Senior Engineer Agent (Opus 4.1)

```bash
# Create senior engineer agent
claude-code agent create senior-engineer \
  --model claude-opus-4-20250805 \
  --instructions .claude/agents/senior-engineer/instructions.md \
  --context "docs/architecture/universal-engineering-principles.md,CLAUDE.md"
```

### 2. Initialize Coding Agent (Sonnet 4)

```bash
# Create coding agent  
claude-code agent create coding-agent \
  --model claude-sonnet-4-20250514 \
  --instructions .claude/agents/coding-agent/instructions.md \
  --context "main.py,test_scripts/,CLAUDE.md"
```

### 3. Usage Commands

```bash
# Senior Engineer: Break down phase document
claude-code agent run senior-engineer \
  "Please analyze the phase document and create detailed TDD task breakdowns for invoice processing improvements. Focus on vendor-agnostic algorithmic patterns."

# Coding Agent: Implement specific task  
claude-code agent run coding-agent \
  "Please implement the task following TDD methodology, ensuring all processing is algorithmic and vendor-agnostic."

# Senior Engineer: Code review
claude-code agent run senior-engineer \
  "Please review the implementation focusing on algorithmic processing patterns and AI service integration."
```

## Workflow Integration

The agents will work together in this flow:

1. **Phase Analysis**: Senior Engineer reads phase document → Creates atomic TDD tasks focused on invoice processing
2. **Implementation**: Coding Agent implements each task following TDD cycle with algorithmic patterns
3. **Review**: Senior Engineer reviews code against engineering principles and invoice processing best practices
4. **Iteration**: Coding Agent addresses feedback until approval

## Key Features of This Setup

**Agent Specialization**:
- **Senior Engineer (Opus 4.1)**: Breaks down phases → Creates detailed invoice processing TDD tasks → Reviews for algorithmic patterns
- **Coding Agent (Sonnet 4)**: Implements TDD tasks → Follows algorithmic processing principles → Requests reviews

**Invoice Processing Focus**: Every task includes comprehensive testing for vendor patterns, AI service integration, and performance within Zapier timeout limits.

**Engineering Principles Compliance**: Both agents are configured to apply the 10 Universal Engineering Principles specifically adapted for invoice processing systems.

**Algorithmic Processing**: Emphasis on pattern-based, vendor-agnostic solutions that scale to new invoice formats.

## Next Steps

1. **Create the agent configurations** using the Claude Code commands above
2. **Place phase documents** in the `docs/phases/` directory
3. **Start with the first phase** - let the Senior Engineer agent break down your phase document into implementable invoice processing tasks
4. **Follow the TDD cycle** - each task implements RED-GREEN-REFACTOR methodology

The agents will work together in a continuous cycle: Senior Engineer creates tasks → Coding Agent implements with TDD → Senior Engineer reviews → iterate until production-ready.

## Critical Success Factors

- **No Hardcoding**: All processing must use algorithmic patterns
- **Multi-tier AI**: Proper fallback from Gemini to Document AI to text parsing
- **Vendor Agnostic**: Code works across invoice formats without modification
- **Performance**: All processing completes within Zapier timeout limits
- **Test Coverage**: Comprehensive testing of all processing patterns and error scenarios