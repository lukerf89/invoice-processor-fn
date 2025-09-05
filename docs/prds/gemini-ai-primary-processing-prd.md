# PRD: Google Gemini AI Primary Processing with Timeout Resolution

## Business Objective
Restore Google Gemini AI as the primary invoice processing method to improve accuracy and speed for shorter invoices while implementing robust timeout resolution strategies to handle longer invoices within Zapier's 160-second limitation. This will reduce manual review time and processing errors while maintaining system reliability across all vendor types.

## Success Criteria
- **Processing accuracy**: Document AI 85% → Gemini AI 95%+ for supported invoice types
- **Processing speed**: Shorter invoices processed in 15-30 seconds vs. 60-90 seconds with Document AI
- **Timeout resolution**: 100% of invoices processed within Zapier 160-second limit
- **System reliability**: 99.5% uptime with graceful fallback to Document AI
- **Manual review reduction**: 15-20 hours saved per week through improved accuracy
- **Vendor coverage**: All current vendors (HarperCollins, Creative-Coop, OneHundred80, Rifle Paper) supported

## Current State Analysis

### Current Processing Flow
1. **Zapier Webhook** receives PDF upload or URL
2. **Gemini AI Processing** (CURRENTLY DISABLED due to timeout issues)
3. **Document AI Fallback** - Primary processing method
   - Document AI Entities extraction
   - Document AI Tables extraction
   - Text-based pattern extraction
4. **Vendor-Specific Processing** for specialized handling
5. **Google Sheets Output** with extracted data

### Current Pain Points
- **Gemini AI Disabled**: Processing bypassed due to timeout issues, losing accuracy benefits
- **Document AI Limitations**: 85% accuracy vs Gemini's 95%+ potential accuracy
- **Processing Speed**: Document AI takes 60-90 seconds even for simple invoices
- **Complex Invoice Timeouts**: Large Creative-Coop invoices cause Zapier timeouts
- **Manual Review Overhead**: 15-20 additional hours/week due to processing errors

### Current Performance Metrics
- **Processing accuracy**: 85% (Document AI only)
- **Average processing time**: 60-90 seconds
- **Timeout rate**: 5-10% on complex invoices when Gemini was enabled
- **Manual review rate**: 35-40% due to accuracy limitations
- **Gemini status**: Completely disabled (line 105 in main.py)

## Requirements

### Functional Requirements

#### FR1: Gemini AI Primary Processing
- **Gemini First Strategy**: Attempt Gemini AI processing for all invoices as primary method
- **Structured JSON Output**: Use existing prompt structure for consistent data extraction
- **Vendor Agnostic Processing**: Handle all vendor types through Gemini's natural language understanding
- **Error Handling**: Graceful degradation when Gemini processing fails

#### FR2: Timeout Resolution Strategies
- **Intelligent PDF Chunking**: Split multi-page invoices into smaller chunks for processing
- **Aggressive Timeout Management**: Hard timeout limits at 30-45 seconds for Gemini processing
- **Fast-Fail Mechanism**: Quick failure detection to allow fallback processing
- **Processing Time Monitoring**: Real-time tracking and optimization

#### FR3: Document AI Fallback Integration
- **Seamless Fallback**: Automatic transition to Document AI when Gemini times out or fails
- **Preservation of Vendor Logic**: Maintain all existing vendor-specific processing capabilities
- **Data Format Consistency**: Ensure identical output format regardless of processing method
- **Error Logging**: Comprehensive logging for timeout analysis and optimization

#### FR4: Multi-Tier Architecture Enhancement
- **Two-Function Deployment Option**: Support both single-function and two-function architectures
- **Smart Routing**: Intelligent decision-making for processing method selection
- **Performance Optimization**: Memory and CPU optimization for different processing paths
- **Monitoring Integration**: Performance tracking across all processing tiers

### Non-Functional Requirements

#### Performance Requirements
- **Zapier Compliance**: 100% of processing must complete within 160-second Zapier timeout
- **Gemini Speed Target**: Simple invoices processed in 15-30 seconds
- **Fallback Speed**: Document AI processing maintains current 60-90 second performance
- **Memory Efficiency**: Processing within current 1GB Cloud Function memory limits

#### Reliability Requirements
- **System Uptime**: 99.5% availability with graceful degradation
- **Error Recovery**: Automatic fallback processing for all failure modes
- **Data Integrity**: 100% consistency in output format across processing methods
- **Monitoring Coverage**: Complete observability for timeout and performance issues

#### Scalability Requirements
- **Volume Handling**: Support 100+ invoices/day across all vendor types
- **Concurrent Processing**: Handle multiple simultaneous invoice requests
- **Resource Scaling**: Automatic scaling based on processing demand
- **Cost Optimization**: Efficient resource utilization to minimize Cloud Function costs

### AI Service Requirements

#### Primary Processing: Gemini AI
- **Model Selection**: Google Gemini 2.5 Flash for optimal accuracy and speed with reduced latency
- **Timeout Management**: 30-45 second hard timeout limits
- **Prompt Optimization**: Enhanced prompts for specific vendor types
- **Error Handling**: Comprehensive failure detection and reporting

#### Secondary Processing: Document AI
- **Fallback Activation**: Automatic activation when Gemini fails or times out
- **Existing Functionality**: Preserve all current Document AI processing capabilities
- **Vendor-Specific Logic**: Maintain specialized processing for all vendors
- **Performance Maintenance**: No degradation in current Document AI performance

#### Tertiary Processing: Text Pattern Extraction
- **Final Fallback**: Text-based extraction when both AI services fail
- **Pattern Maintenance**: Preserve all existing regex and pattern matching logic
- **Vendor Coverage**: Support for all vendor-specific text patterns

### Vendor Support Requirements

#### Current Vendor Maintenance
- **HarperCollins**: Perfect PO processing with ISBN extraction and 50% discount calculation
- **Creative-Coop**: Phase 02 enhanced multi-tier processing with sophisticated pattern matching
- **OneHundred80**: Logic-based processing with UPC codes and enhanced descriptions
- **Rifle Paper**: Custom description cleaning and line item extraction

#### Enhanced Gemini Processing
- **Natural Language Understanding**: Leverage Gemini's advanced language capabilities for vendor-specific formats
- **Context Awareness**: Intelligent handling of different invoice layouts and structures
- **Adaptive Processing**: Self-improving accuracy through natural language processing
- **Fallback Preservation**: Maintain all existing vendor-specific fallback logic

## Technical Implementation Strategy

### Implementation Approach Options

#### Option A: Enhanced Single Function (Recommended)
**Architecture**: Enhance existing `process_invoice` function with intelligent Gemini timeout management
- **Pros**: Simple deployment, existing infrastructure, easier maintenance
- **Cons**: Single point of failure, more complex timeout handling
- **Timeline**: 2-3 weeks implementation
- **Risk**: Medium - requires sophisticated timeout management

#### Option B: Two-Function Architecture
**Architecture**: Deploy separate Gemini-optimized and Document AI functions with Zapier orchestration
- **Pros**: Clear separation of concerns, optimized resource allocation, better timeout isolation
- **Cons**: More complex Zapier configuration, dual deployment maintenance
- **Timeline**: 3-4 weeks implementation
- **Risk**: Low - proven fallback methodology

### Recommended Implementation: Option A with Fallback Support

#### Phase 1: Timeout Resolution Foundation (Week 1)
1. **Gemini Timeout Management**
   - Implement 30-second hard timeout for Gemini processing
   - Add processing time monitoring and logging
   - Create fast-fail mechanisms for immediate fallback
   - Test timeout behavior with sample invoices

2. **PDF Analysis and Chunking**
   - Analyze PDF size and page count before processing
   - Implement intelligent chunking strategy for large invoices
   - Create size-based processing routing logic
   - Test chunking with Creative-Coop holiday invoices

#### Phase 2: Gemini AI Re-enablement (Week 2)
1. **Enhanced Gemini Processing**
   - Re-enable Gemini AI in `process_with_gemini_first` function
   - Implement timeout-aware processing logic
   - Add comprehensive error handling and logging
   - Optimize prompts for different vendor types

2. **Fallback Integration Testing**
   - Test Gemini → Document AI fallback flow
   - Validate data format consistency
   - Ensure vendor-specific processing preservation
   - Performance testing across all invoice types

#### Phase 3: Production Deployment and Monitoring (Week 3)
1. **Production Rollout**
   - Gradual rollout with monitoring
   - A/B testing with current Document AI processing
   - Performance metrics collection and analysis
   - Error rate monitoring and optimization

2. **Two-Function Architecture Preparation** (Optional)
   - Prepare separate function deployment if needed
   - Create Zapier integration templates
   - Document deployment procedures for both architectures

### Technical Specifications

#### Gemini Processing Enhancements
```python
def process_with_gemini_enhanced(pdf_content):
    """Enhanced Gemini processing with timeout management"""
    import time

    start_time = time.time()
    timeout_limit = 30  # seconds

    try:
        # PDF size analysis
        pdf_size = len(pdf_content)
        if pdf_size > 5_000_000:  # 5MB threshold
            print(f"⚠️ Large PDF ({pdf_size/1024/1024:.1f}MB) - using chunking strategy")
            return process_with_chunking(pdf_content)

        # Standard Gemini processing with timeout monitoring
        response = model.generate_content([prompt, pdf_content])

        processing_time = time.time() - start_time
        if processing_time > timeout_limit:
            print(f"⚠️ Gemini timeout: {processing_time:.1f}s > {timeout_limit}s")
            return None  # Trigger fallback

        return parse_gemini_response(response)

    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Gemini failed after {processing_time:.1f}s: {e}")
        return None  # Trigger fallback
```

#### PDF Chunking Strategy
```python
def process_with_chunking(pdf_content):
    """Process large PDFs in chunks to avoid timeouts"""

    # Split PDF into pages or logical sections
    chunks = split_pdf_intelligent(pdf_content)

    results = []
    for i, chunk in enumerate(chunks):
        chunk_result = process_chunk_with_timeout(chunk, timeout=20)
        if chunk_result:
            results.append(chunk_result)
        else:
            print(f"⚠️ Chunk {i+1} failed, continuing with Document AI fallback")
            return None

    # Combine results from all chunks
    return combine_chunk_results(results)
```

## Constraints & Assumptions

### Technical Constraints
- **Zapier 160-second timeout**: Hard limit that cannot be exceeded
- **Google Cloud Function limits**: 1GB memory, 540-second function timeout
- **Google Sheets API limits**: Rate limiting for concurrent writes
- **Gemini API limits**: Processing time variability based on PDF complexity
- **Document AI processing**: Current 60-90 second processing time baseline

### Business Constraints
- **Zero downtime requirement**: Cannot disrupt current production processing
- **Backward compatibility**: Must maintain all existing vendor-specific processing
- **Cost optimization**: Cannot significantly increase Cloud Function costs
- **Accuracy maintenance**: Cannot reduce current 85% processing accuracy

### Technical Assumptions
- **Gemini performance**: Consistently faster than Document AI for invoices < 3 pages
- **PDF complexity correlation**: Processing time correlates with PDF size and page count
- **Timeout predictability**: Can reliably detect and handle timeout conditions
- **Fallback reliability**: Document AI processing remains stable and available

### Business Assumptions
- **User acceptance**: Improved accuracy and speed will reduce manual review needs
- **Invoice characteristics**: 70-80% of invoices are suitable for fast Gemini processing
- **Vendor stability**: Current vendor-specific patterns remain consistent
- **Volume growth**: Invoice processing volume will increase with improved accuracy

## Risk Assessment

### High Risk Items
1. **Timeout Detection Accuracy**
   - **Risk**: Inconsistent timeout behavior leading to Zapier failures
   - **Impact**: Service disruption and processing failures
   - **Mitigation**: Extensive testing with various invoice types, conservative timeout limits

2. **Gemini API Reliability**
   - **Risk**: Gemini service degradation or unavailability
   - **Impact**: Complete fallback to Document AI processing
   - **Mitigation**: Robust fallback mechanisms, API health monitoring

3. **PDF Chunking Complexity**
   - **Risk**: Chunking strategy fails to maintain invoice context
   - **Impact**: Reduced accuracy for complex invoices
   - **Mitigation**: Intelligent chunking algorithms, extensive testing with Creative-Coop invoices

### Medium Risk Items
1. **Performance Variability**
   - **Risk**: Inconsistent processing times affecting timeout management
   - **Impact**: Suboptimal routing decisions and occasional timeouts
   - **Mitigation**: Comprehensive performance monitoring and adaptive timeout adjustment

2. **Integration Complexity**
   - **Risk**: Complex timeout management affecting code maintainability
   - **Impact**: Increased technical debt and maintenance overhead
   - **Mitigation**: Clean architectural separation, comprehensive testing

### Dependencies
- **Gemini API Availability**: Google Gemini service reliability and performance
- **Document AI Stability**: Continued reliability of fallback processing
- **Zapier Configuration**: Proper webhook timeout and retry configuration
- **Google Cloud Platform**: Function deployment and scaling capabilities

## Implementation Phases

### Phase 1: Foundation and Analysis (Week 1)
**Deliverables:**
- [ ] PDF size analysis and routing logic
- [ ] Gemini timeout management implementation
- [ ] Enhanced error handling and logging
- [ ] Initial chunking strategy for large PDFs

**Success Criteria:**
- [ ] Timeout detection works reliably across invoice types
- [ ] PDF size-based routing correctly identifies complex invoices
- [ ] Logging provides comprehensive processing insights
- [ ] Chunking strategy preserves invoice context

### Phase 2: Gemini Re-enablement (Week 2)
**Deliverables:**
- [ ] Re-enabled Gemini processing with timeout safeguards
- [ ] Enhanced prompts optimized for vendor types
- [ ] Comprehensive fallback testing
- [ ] Performance benchmarking across all vendors

**Success Criteria:**
- [ ] Gemini processes 70%+ of invoices successfully within timeout
- [ ] Fallback triggers correctly for complex invoices
- [ ] Processing accuracy meets or exceeds 95% for Gemini-processed invoices
- [ ] All vendor-specific logic preserved in fallback processing

### Phase 3: Production Deployment (Week 3)
**Deliverables:**
- [ ] Production deployment with monitoring
- [ ] Performance metrics dashboard
- [ ] A/B testing framework for comparison
- [ ] Documentation and runbooks

**Success Criteria:**
- [ ] Zero Zapier timeouts in production
- [ ] 95%+ processing accuracy achieved
- [ ] 20%+ reduction in processing time for simple invoices
- [ ] Comprehensive monitoring and alerting in place

### Phase 4: Optimization and Two-Function Option (Week 4)
**Deliverables:**
- [ ] Performance optimization based on production data
- [ ] Two-function architecture option ready for deployment
- [ ] Advanced chunking strategies for complex invoices
- [ ] Long-term monitoring and maintenance procedures

**Success Criteria:**
- [ ] Processing performance optimized based on real usage
- [ ] Two-function deployment option fully tested and documented
- [ ] Advanced handling for edge cases and complex invoices
- [ ] Sustainable monitoring and maintenance procedures established

## Acceptance Criteria

### Core Processing Requirements
- [ ] **Timeout Compliance**: 100% of processing completes within Zapier 160-second limit
- [ ] **Accuracy Target**: 95%+ line item extraction accuracy for Gemini-processed invoices
- [ ] **Fallback Reliability**: Document AI processing maintains current 85% accuracy
- [ ] **Speed Improvement**: 20%+ faster processing for simple invoices (< 3 pages)

### Vendor Coverage Requirements
- [ ] **HarperCollins**: Perfect PO processing preserved with enhanced Gemini accuracy
- [ ] **Creative-Coop**: Phase 02 multi-tier processing maintained with improved speed
- [ ] **OneHundred80**: Logic-based processing enhanced with Gemini natural language understanding
- [ ] **Rifle Paper**: Description cleaning and extraction improved through Gemini processing

### System Reliability Requirements
- [ ] **Error Handling**: All failure modes handled gracefully with appropriate fallbacks
- [ ] **Monitoring**: Comprehensive logging and metrics for timeout analysis and optimization
- [ ] **Performance**: Processing time monitoring and optimization based on real usage data
- [ ] **Documentation**: Complete technical documentation and operational runbooks

### Business Impact Requirements
- [ ] **Manual Review Reduction**: 15-20 hours per week saved through improved accuracy
- [ ] **Processing Consistency**: Identical output format regardless of processing method
- [ ] **Cost Efficiency**: No significant increase in Cloud Function operational costs
- [ ] **User Experience**: Transparent processing improvements with no workflow disruption

### Advanced Features (Future Enhancement)
- [ ] **Intelligent Routing**: Smart selection of processing method based on invoice characteristics
- [ ] **Adaptive Timeouts**: Dynamic timeout adjustment based on invoice complexity
- [ ] **Processing Analytics**: Detailed insights into processing performance and optimization opportunities
- [ ] **Vendor Pattern Learning**: Self-improving accuracy through processing pattern analysis

## Monitoring and Success Metrics

### Key Performance Indicators
- **Processing Success Rate**: Target 99.5% successful processing
- **Timeout Rate**: Target 0% Zapier timeouts
- **Processing Speed**: Target 20%+ improvement for simple invoices
- **Accuracy Rate**: Target 95%+ for Gemini processing, 85%+ overall
- **Manual Review Rate**: Target 20% reduction from current levels

### Monitoring Infrastructure
- **Processing Time Tracking**: Real-time monitoring of all processing stages
- **Error Rate Analysis**: Detailed categorization of failure types and causes
- **Vendor Performance Metrics**: Processing success and accuracy by vendor type
- **Resource Utilization**: Memory and CPU usage optimization tracking

### Business Impact Tracking
- **Manual Review Hours**: Weekly tracking of time saved through improved accuracy
- **Processing Volume**: Invoice processing capacity and scalability metrics
- **User Satisfaction**: Feedback on processing speed and accuracy improvements
- **Cost Analysis**: Cloud Function resource costs and optimization opportunities

This PRD provides a comprehensive roadmap for implementing Gemini AI as the primary processing method while maintaining system reliability and addressing timeout constraints. The phased approach ensures minimal risk while maximizing the benefits of improved AI processing capabilities.

