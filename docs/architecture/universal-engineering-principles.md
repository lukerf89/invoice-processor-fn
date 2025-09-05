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
- Implement idempotent operations where possible (reprocessing same invoice should not duplicate entries)

**Implementation Examples:**
```python
def process_with_retry(operation, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return operation()
        except TransientError as e:
            if attempt == max_attempts - 1:
                logger.error(f"Operation failed after {max_attempts} attempts: {e}")
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## 2. Scalability (Designed for Volume Growth)

**Rules:**
- Process invoices asynchronously when possible
- Batch similar vendor invoices for efficiency
- Favor **horizontal scaling** through Cloud Functions
- Architect for "N+1 growth" — assume invoice volume doubles yearly
- Optimize for Zapier timeout limits (160 seconds)
- Use streaming processing for large PDF files
- Implement request queuing to handle traffic spikes

**Performance Targets:**
- Process standard invoice (< 5MB) in under 60 seconds
- Handle 10 concurrent invoice processing requests
- Memory usage should not exceed 1GB per processing instance
- Support processing 1000+ invoices per day

---

## 3. Security (Trust Requires Safety)

**Rules:**
- Handle PDF files safely without file system exposure
- Encrypt invoice data both at rest and in transit
- Keep API keys in Google Secret Manager, never in code
- Audit access to sensitive invoice data
- Validate PDF content before processing to prevent malicious files
- Sanitize all extracted data before storage
- Use least-privilege access for all service accounts
- Log security events for audit trails

**Security Checklist:**
- [ ] No secrets in code or logs
- [ ] PDF processing sandboxed
- [ ] Input validation on all extracted data
- [ ] Secure transmission to Google Sheets
- [ ] Access logging for all operations

---

## 4. Maintainability (Ease of Understanding & Adaptation)

**Rules:**
- Use **algorithmic patterns** instead of hardcoded vendor-specific logic
- Log structured events with invoice processing context
- Keep vendor processing modular — failed Creative-Coop logic shouldn't affect HarperCollins
- Use consistent naming patterns for extraction functions
- Favor "pattern-based logic" over hardcoded mappings
- Document all vendor-specific patterns with examples
- Create reusable functions for common operations
- Maintain clear separation between AI service calls and business logic

**Code Organization:**
```python
# ✅ GOOD: Algorithmic pattern
def extract_quantity_pattern(text):
    """Extract quantity using pattern matching"""
    pattern = r'(\d+)\s+\d+\s+\w+\s+each'
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0

# ❌ BAD: Hardcoded logic
def get_creative_coop_quantity(product_code):
    hardcoded_quantities = {"DF6802": 8, "ST1234": 5}
    return hardcoded_quantities.get(product_code, 0)
```

---

## 5. Observability (See What the System Processes)

**Rules:**
- Dashboards must display **business KPIs mapped to system health:**
  - Invoices processed successfully
  - Document AI vs Gemini success rates
  - Line item extraction accuracy per vendor
  - Processing time per vendor type
  - Error rates and failure modes
- Critical alerts include:
  - AI service failures or timeouts
  - Low extraction confidence scores (< 80%)
  - Vendor pattern recognition failures
  - Performance degradation (> 120s processing time)
- Logging must support **traceability across invoices** (correlation IDs)
- Track accuracy metrics against known ground truth

**Structured Logging Example:**
```python
logger.info("Invoice processing completed", extra={
    'correlation_id': correlation_id,
    'invoice_vendor': vendor_type,
    'processing_time_ms': elapsed_time,
    'line_items_extracted': len(results),
    'processing_tier': 'document_ai',
    'accuracy_score': confidence_score
})
```

---

## 6. Resilience & Fault Tolerance (Systems Adapt, Don't Break)

**Rules:**
- Always assume AI service failure (Document AI, Gemini outages)
- Use **multi-tier fallback**: Gemini → Document AI → Text parsing
- Design fallbacks for vendor-specific patterns
- Test recovery patterns with deliberate AI service failures
- Maintain **manual processing capability** when automation fails
- Implement graceful degradation — partial success is better than total failure
- Use dead letter queues for failed processing attempts
- Implement health checks for all external dependencies

**Resilience Implementation:**
```python
def process_invoice_with_fallback(document):
    """Multi-tier processing with fallback"""
    processing_tiers = [
        ('gemini', process_with_gemini_first),
        ('document_ai_entities', extract_line_items_from_entities),
        ('document_ai_tables', extract_line_items),
        ('text_parsing', extract_line_items_from_text)
    ]

    for tier_name, processor in processing_tiers:
        try:
            result = processor(document)
            if result:
                logger.info(f"Successfully processed with {tier_name}")
                return result
        except Exception as e:
            logger.warning(f"Processing tier {tier_name} failed: {e}")
            continue

    raise ProcessingError("All processing tiers failed")
```

---

## 7. Future-Proofing (Freedom to Evolve)

**Rules:**
- Vendor processing patterns live in algorithmic functions, not hardcoded mappings
- Build with **new vendor adaptability**: patterns should extend easily
- Use **cloud-native services** for portability
- Document assumptions about current vendors (today's Creative-Coop → tomorrow's new vendors)
- Keep business logic separate from AI service implementations
- Design APIs that can accommodate new data fields
- Version control all processing patterns for rollback capability
- Plan for AI model upgrades and changes

**Extensible Design:**
```python
class VendorProcessor:
    """Base class for vendor-specific processing"""
    def extract_line_items(self, document):
        raise NotImplementedError

    def detect_vendor(self, text):
        raise NotImplementedError

class CreativeCoopProcessor(VendorProcessor):
    """Algorithmic processing for Creative-Coop invoices"""
    def extract_line_items(self, document):
        # Use patterns, not hardcoded values
        return self._extract_using_patterns(document)
```

---

## 8. Simplicity (Complexity is a Liability)

**Rules:**
- Prefer algorithmic patterns that solve invoice problems without vendor-specific abstraction
- Every vendor-specific function must justify its existence
- Avoid "clever" extraction code — optimize for pattern readability
- Regularly refactor before adding new vendors
- Use existing libraries for common operations (regex, date parsing, etc.)
- Keep functions small and focused on single responsibilities
- Minimize dependencies — each dependency is a potential failure point

**Simplicity Examples:**
```python
# ✅ SIMPLE: Clear, readable pattern
def extract_price_from_line(line_text):
    """Extract price using simple regex"""
    price_pattern = r'\$(\d+\.\d{2})'
    match = re.search(price_pattern, line_text)
    return float(match.group(1)) if match else 0.0

# ❌ COMPLEX: Over-engineered solution
class PriceExtractionEngine:
    def __init__(self):
        self.price_extractors = [
            ComplexPriceExtractor(),
            AdvancedPriceExtractor(),
            FallbackPriceExtractor()
        ]
    # ... unnecessary complexity
```

---

## 9. Testability (Systems Must Prove Accuracy)

**Rules:**
- Every invoice processing function must be testable with mock data
- Unit/integration tests required for all vendor patterns
- Test environments must use real invoice samples (anonymized)
- Automate accuracy regression testing after changes
- Use test-driven development (TDD) for all new features
- Maintain comprehensive test fixtures for each vendor type
- Test error scenarios and edge cases extensively
- Measure and track test coverage (minimum 90% for business logic)

**Testing Strategy:**
```python
class TestCreativeCoopProcessing:
    def test_quantity_extraction_pattern(self):
        """Test quantity extraction with various patterns"""
        test_cases = [
            ("DF6802 8 0 lo each $12.50", 8),
            ("ST1234 12 5 Set $8.00", 12),
            ("AB9999 1 0 Case $15.00", 1)
        ]

        for text, expected_qty in test_cases:
            result = extract_creative_coop_quantity(text)
            assert result == expected_qty, f"Failed for: {text}"

    def test_handles_malformed_input(self):
        """Test graceful handling of malformed data"""
        malformed_inputs = ["", "invalid text", "DF6802 invalid quantity"]

        for invalid_input in malformed_inputs:
            result = extract_creative_coop_quantity(invalid_input)
            assert isinstance(result, int), "Should return integer even for invalid input"
            assert result >= 0, "Should return non-negative quantity"
```

---

## 10. Documentation & Knowledge Sharing (Processing Memory)

**Rules:**
- Every vendor processing function includes purpose, inputs, outputs, accuracy metrics
- Critical patterns require change logs (who changed what extraction logic, why)
- Prefer **living documentation** (auto-generated from test cases) over static docs
- Build team confidence: new vendor patterns take < 2 days to implement following patterns
- Document all assumptions and edge cases
- Maintain runbooks for common issues and their solutions
- Create examples for each vendor type showing expected inputs/outputs
- Keep architecture decisions recorded with rationale

**Documentation Examples:**
```python
def extract_creative_coop_quantity(text):
    """
    Extract ordered quantity from Creative-Coop invoice line items.

    Pattern: "DF6802 8 0 lo each $12.50 $100.00"
    Where: [product_code] [ordered_qty] [backordered_qty] [unit] [unit_type] [unit_price] [total]

    Args:
        text (str): Line item text from invoice

    Returns:
        int: Ordered quantity, 0 if pattern not found

    Accuracy: 95% on test dataset (24/25 items correctly extracted)
    Last Updated: 2024-01-15

    Examples:
        >>> extract_creative_coop_quantity("DF6802 8 0 lo each $12.50")
        8
        >>> extract_creative_coop_quantity("ST1234 12 5 Set $8.00")
        12
    """
    pattern = r'^\w+\s+(\d+)\s+\d+\s+\w+\s+\w+\s+\$[\d\.]+.*$'
    match = re.search(pattern, text.strip())
    return int(match.group(1)) if match else 0
```

---

## Practical Example Engineered Inside These Principles

**Scenario**: If Document AI fails to extract Creative-Coop line items:

1. **Reliability**: System retries Document AI call 3 times with exponential backoff
2. **Resilience**: After retries fail, falls back to text-based pattern extraction
3. **Observability**: Logs structured error with invoice context and correlation ID
4. **Maintainability**: Uses algorithmic quantity extraction patterns, not hardcoded logic
5. **Fault Tolerance**: Processing continues for other line items even if some fail
6. **Simplicity**: Uses clear regex patterns that are easy to understand and modify
7. **Testability**: All extraction patterns are unit tested with known inputs/outputs
8. **Security**: Extracted data is validated before being written to Google Sheets
9. **Performance**: Entire fallback process completes within Zapier timeout limits
10. **Documentation**: Pattern extraction logic is documented with examples and accuracy metrics

**Code Implementation:**
```python
def process_creative_coop_with_principles(document, correlation_id):
    """Process Creative-Coop invoice following all 10 engineering principles"""

    try:
        # Reliability: Retry with exponential backoff
        result = retry_with_backoff(
            lambda: extract_line_items_from_entities(document),
            max_attempts=3
        )

        if result:
            # Observability: Log success
            logger.info("Document AI extraction successful", extra={
                'correlation_id': correlation_id,
                'vendor': 'creative-coop',
                'items_extracted': len(result)
            })
            return result

    except Exception as e:
        # Resilience: Fall back to algorithmic extraction
        logger.warning("Document AI failed, using pattern extraction", extra={
            'correlation_id': correlation_id,
            'error': str(e)
        })

        # Maintainability: Use algorithmic patterns
        result = extract_creative_coop_patterns(document.text)

        # Security: Validate extracted data
        validated_result = validate_line_items(result)

        return validated_result
```

This implementation demonstrates how all 10 principles work together to create robust, maintainable invoice processing systems.
