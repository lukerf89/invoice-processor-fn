# Two-Tier Fallback Plan for Invoice Processing

## Current Issue
Zapier webhooks timeout after 160 seconds when Gemini AI takes too long to process invoices, preventing any fallback to Document AI.

## Proposed Solution: Dual Function Architecture

### Architecture Overview
Deploy two separate Cloud Functions that Zapier calls sequentially:

1. **`process-invoice-gemini`** - Fast Gemini-only processing
2. **`process-invoice-fallback`** - Reliable Document AI processing

### Function 1: process-invoice-gemini
**Purpose**: Quick Gemini AI processing with aggressive timeout
- **Timeout**: 30-45 seconds max
- **Memory**: 512MB (lighter footprint)
- **Behavior**: 
  - Try Gemini AI with short timeout
  - Return success or explicit failure (no fallback)
  - Optimized for speed over reliability

### Function 2: process-invoice-fallback  
**Purpose**: Reliable Document AI processing (current system)
- **Timeout**: 540 seconds (current)
- **Memory**: 1GB (current)  
- **Behavior**: 
  - Skip Gemini entirely
  - Use proven Document AI + vendor-specific processing
  - Guaranteed to work within Zapier limits

### Zapier Workflow Configuration
```
1. POST to process-invoice-gemini
   ├─ Success (HTTP 200) → DONE ✅
   └─ Failure/Timeout → Continue to Step 2

2. POST to process-invoice-fallback  
   ├─ Success (HTTP 200) → DONE ✅
   └─ Failure → Log error ❌
```

## Detailed Implementation Steps

### Phase 1: Create Gemini-Optimized Function

#### Step 1.1: Create New Directory Structure
```bash
# Create new Gemini-only function directory
mkdir -p ../invoice-processor-gemini-only
cd ../invoice-processor-gemini-only

# Copy essential files
cp ../invoice-processor-fn/main.py ./main_gemini.py
cp ../invoice-processor-fn/requirements.txt ./requirements.txt
```

#### Step 1.2: Modify main_gemini.py for Gemini-only Processing
```python
import json
import os
import time
from datetime import datetime
import functions_framework
import google.generativeai as genai
import requests
from flask import Request, jsonify
from google.auth import default
from googleapiclient.discovery import build

@functions_framework.http
def process_invoice_gemini(request: Request):
    """Gemini-only invoice processing with aggressive timeout"""
    
    # Same file handling as original...
    
    # GEMINI PROCESSING ONLY - NO FALLBACKS
    start_time = time.time()
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"success": False, "error": "Gemini API key not found"}), 500
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Aggressive timeout - fail fast
        response = model.generate_content([
            prompt,
            {"mime_type": "application/pdf", "data": pdf_content}
        ])
        
        processing_time = time.time() - start_time
        
        # Hard timeout check - fail if too slow
        if processing_time > 30:
            return jsonify({
                "success": False, 
                "error": f"Gemini timeout: {processing_time:.1f}s > 30s limit",
                "processing_time": processing_time
            }), 408  # Request Timeout
        
        # Process Gemini response...
        # Write to Google Sheets...
        
        return jsonify({
            "success": True,
            "method": "gemini",
            "processing_time": processing_time,
            "items_processed": len(rows)
        })
        
    except Exception as e:
        processing_time = time.time() - start_time
        return jsonify({
            "success": False,
            "error": f"Gemini processing failed: {str(e)}",
            "processing_time": processing_time
        }), 500
```

#### Step 1.3: Update requirements.txt for Gemini-only
```txt
functions-framework
google-generativeai>=0.3.0
requests
flask
google-auth
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

#### Step 1.4: Deploy Gemini Function
```bash
gcloud functions deploy process-invoice-gemini \
    --gen2 \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=512MB \
    --timeout=45s \
    --region=us-central1 \
    --entry-point=process_invoice_gemini \
    --source=. \
    --set-env-vars="GOOGLE_CLOUD_PROJECT_ID=freckled-hen-analytics,GOOGLE_SHEETS_SPREADSHEET_ID=1PdnZGPZwAV6AHXEeByhOlaEeGObxYWppwLcq0gdvs0E,GOOGLE_SHEETS_SHEET_NAME=Update 20230525" \
    --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"
```

### Phase 2: Update Fallback Function

#### Step 2.1: Rename Current Function
```bash
# Current function becomes the fallback
gcloud functions deploy process-invoice-fallback \
    --gen2 \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=1GiB \
    --timeout=540s \
    --region=us-central1 \
    --entry-point=process_invoice \
    --source=. \
    --set-env-vars="GOOGLE_CLOUD_PROJECT_ID=freckled-hen-analytics,DOCUMENT_AI_PROCESSOR_ID=be53c6e3a199a473,GOOGLE_CLOUD_LOCATION=us,GOOGLE_SHEETS_SPREADSHEET_ID=1PdnZGPZwAV6AHXEeByhOlaEeGObxYWppwLcq0gdvs0E,GOOGLE_SHEETS_SHEET_NAME=Update 20230525"
    # Note: No Gemini API key - pure Document AI
```

#### Step 2.2: Modify main.py for Fallback-only
```python
def process_with_gemini_first(pdf_content):
    """REMOVED - No Gemini in fallback function"""
    return None

@functions_framework.http  
def process_invoice(request: Request):
    """Document AI only - reliable fallback processing"""
    
    # Skip Gemini entirely - go straight to Document AI
    print("📄 Using Document AI processing (fallback function)")
    
    # ... rest of Document AI processing ...
    
    return jsonify({
        "success": True,
        "method": "document_ai_fallback", 
        "vendor": vendor,
        "items_processed": len(rows)
    })
```

### Phase 3: Zapier Configuration

#### Step 3.1: Configure Primary Webhook
```
URL: https://us-central1-freckled-hen-analytics.cloudfunctions.net/process-invoice-gemini
Method: POST
Timeout: 45 seconds
Headers: Content-Type: application/json
Body: {"file_url": "{{invoice_url}}"}
```

#### Step 3.2: Configure Fallback Webhook (Error Handler)
```
Trigger: Only if first webhook fails/times out
URL: https://us-central1-freckled-hen-analytics.cloudfunctions.net/process-invoice-fallback  
Method: POST
Timeout: 160 seconds
Headers: Content-Type: application/json
Body: {"file_url": "{{invoice_url}}"}
```

#### Step 3.3: Zapier Flow Logic
```
1. Try Gemini Function
   ├─ HTTP 200 + "success": true → DONE ✅
   ├─ HTTP 408 (timeout) → Continue to Fallback
   ├─ HTTP 500 (error) → Continue to Fallback  
   └─ No response (timeout) → Continue to Fallback

2. Try Fallback Function
   ├─ HTTP 200 + "success": true → DONE ✅
   └─ Any failure → Log error and stop ❌
```

### Phase 4: Testing & Validation

#### Step 4.1: Function Testing
```bash
# Test Gemini function with simple invoice
curl -X POST "https://us-central1-freckled-hen-analytics.cloudfunctions.net/process-invoice-gemini" \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/simple-invoice.pdf"}' \
  --max-time 45

# Test fallback function with complex invoice  
curl -X POST "https://us-central1-freckled-hen-analytics.cloudfunctions.net/process-invoice-fallback" \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/complex-invoice.pdf"}' \
  --max-time 160
```

#### Step 4.2: Zapier Integration Testing
1. **Simple Invoice Test**: Should complete via Gemini function
2. **Complex Invoice Test**: Should timeout on Gemini, succeed on fallback
3. **Large Invoice Test**: Should use fallback function successfully
4. **Invalid PDF Test**: Should fail gracefully on both functions

### Phase 5: Monitoring & Optimization

#### Step 5.1: Add Detailed Logging
```python
# In both functions, add performance metrics
log_data = {
    "function_type": "gemini" or "fallback",
    "processing_time": processing_time,
    "success": True/False,
    "vendor": vendor,
    "items_extracted": len(rows),
    "file_size_estimate": len(pdf_content),
    "timestamp": datetime.now().isoformat()
}
print(f"📊 METRICS: {json.dumps(log_data)}")
```

#### Step 5.2: Success Rate Tracking
```bash
# Query logs to track success rates
gcloud logging read "resource.type=cloud_function AND (
    resource.labels.function_name=process-invoice-gemini OR 
    resource.labels.function_name=process-invoice-fallback
) AND textPayload:METRICS" \
    --format="csv(timestamp,resource.labels.function_name,textPayload)" \
    --freshness=7d > invoice_processing_metrics.csv
```

## Benefits

### Reliability
- ✅ Guaranteed processing within Zapier timeout limits
- ✅ Best of both worlds: fast Gemini + reliable Document AI
- ✅ No single point of failure

### Performance  
- ✅ Fast invoices get Gemini speed/accuracy
- ✅ Complex invoices get Document AI reliability
- ✅ Independent scaling for each approach

### Debugging
- ✅ Clear separation - can see which method worked
- ✅ Independent logs for each processing tier
- ✅ Easier to optimize each function separately

## Deployment Configuration

### process-invoice-gemini
```bash
gcloud functions deploy process-invoice-gemini \
    --gen2 \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=512MB \
    --timeout=45s \
    --region=us-central1 \
    --entry-point=process_invoice_gemini \
    --set-env-vars="..." \
    --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"
```

### process-invoice-fallback  
```bash
gcloud functions deploy process-invoice-fallback \
    --gen2 \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=1GiB \
    --timeout=540s \
    --region=us-central1 \
    --entry-point=process_invoice_fallback \
    --set-env-vars="..."
    # No Gemini API key needed
```

## Future Enhancements

### Smart Routing
Could add logic to determine which function to try first based on:
- Invoice file size
- Vendor type (some work better with Gemini vs Document AI)
- Historical success rates

### Monitoring
- Track success rates for each function
- Monitor processing times
- Optimize timeout values based on real usage

### Cost Optimization
- Gemini function uses less memory/time = lower cost for simple invoices
- Document AI function only used when needed

## Implementation Timeline

### Week 1: Preparation (2-3 hours)
- [ ] Create Gemini-only function codebase
- [ ] Remove Document AI dependencies from Gemini function
- [ ] Add aggressive timeout logic
- [ ] Test Gemini function locally

### Week 2: Deployment (2-3 hours)  
- [ ] Deploy process-invoice-gemini function
- [ ] Deploy process-invoice-fallback function  
- [ ] Test both functions independently
- [ ] Verify Google Sheets integration works for both

### Week 3: Zapier Integration (1-2 hours)
- [ ] Configure Zapier primary webhook (Gemini)
- [ ] Configure Zapier fallback webhook (Document AI)
- [ ] Test with variety of invoice types
- [ ] Monitor success/failure rates

### Week 4: Optimization (1-2 hours)
- [ ] Analyze performance metrics
- [ ] Adjust timeout values based on real usage
- [ ] Fine-tune memory allocation
- [ ] Document final configuration

## Cost Analysis

### Current Single Function Cost
- **Memory**: 1GB × processing time
- **Compute**: Full processing regardless of complexity
- **Document AI**: Always used (after Gemini timeout)

### Two-Tier Function Cost  
- **Simple invoices**: 512MB × 10-30s (Gemini only) = **60-70% cost reduction**
- **Complex invoices**: 512MB × 30s + 1GB × 60s = **Similar cost**
- **Document AI**: Only used when Gemini fails = **Potential 40-50% reduction**

**Estimated Monthly Savings**: $50-200 depending on invoice mix

## Risk Assessment

### High Risk Items
- **Zapier configuration complexity**: Mitigation = thorough testing
- **Function deployment issues**: Mitigation = gradual rollout
- **Data consistency between functions**: Mitigation = shared libraries

### Medium Risk Items
- **Timeout tuning**: May require iteration based on real usage
- **Cost optimization**: Monitor billing during first month
- **Monitoring setup**: Need proper alerting for failures

### Low Risk Items  
- **Code functionality**: Based on proven existing code
- **Google Sheets integration**: Already working
- **Authentication**: Uses existing service accounts

## Success Metrics

### Primary Goals (Must Achieve)
- [ ] **Zero Zapier timeouts** with two-tier approach
- [ ] **>95% processing success rate** across all invoice types  
- [ ] **Faster processing** for simple invoices (Gemini)
- [ ] **Reliable fallback** for complex invoices

### Secondary Goals (Nice to Have)
- [ ] **30-50% cost reduction** from optimized processing
- [ ] **Better debugging** with separate function logs
- [ ] **Performance insights** from detailed metrics
- [ ] **Scalability improvements** with independent functions

## Rollback Plan

### Emergency Rollback (if critical issues)
```bash
# Immediate: Point Zapier back to current working function
# Update Zapier webhook URL to: 
https://us-central1-freckled-hen-analytics.cloudfunctions.net/process_invoice

# This restores full functionality within 5 minutes
```

### Graceful Rollback (if optimization needed)
1. **Keep both functions running**
2. **Gradually shift traffic** back to single function
3. **Analyze what went wrong** using logs and metrics  
4. **Fix issues** and re-attempt deployment
5. **Delete unused functions** once satisfied with rollback

### Function Cleanup (after successful rollback)
```bash
# Remove the two-tier functions if no longer needed
gcloud functions delete process-invoice-gemini --region=us-central1
gcloud functions delete process-invoice-fallback --region=us-central1
```

## Maintenance Plan

### Weekly Monitoring
- Check success rates for both functions
- Monitor processing times and timeout rates
- Review Google Sheets data quality
- Analyze cost optimization opportunities

### Monthly Review
- Adjust timeout values based on performance data
- Optimize memory allocation for cost efficiency
- Update Gemini prompts if needed
- Review vendor-specific processing accuracy

### Quarterly Enhancement
- Evaluate new Gemini model versions
- Consider adding smart routing logic
- Implement additional vendor-specific optimizations
- Review and update documentation

---

**Status**: Ready for Implementation  
**Priority**: Medium-High (implement when ready to re-enable Gemini)  
**Estimated Total Effort**: 8-12 hours over 4 weeks  
**Estimated Monthly Savings**: $50-200  
**Risk Level**: Medium (with proper testing)  
**Rollback Time**: 5 minutes (emergency) / 1-2 hours (graceful)