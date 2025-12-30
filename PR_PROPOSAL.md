# PR Proposal: Enable "Remove Expired Delete Markers" Lifecycle Rule for Versioned S3 Buckets

## 📋 Summary

**Proposal:** Enable lifecycle rules to automatically remove expired delete markers in versioned S3 buckets to reduce storage costs and improve bucket performance.

**Status:** Ready for review (pending code freeze completion)  
**Priority:** Medium  
**Impact:** Cost optimization and operational improvement

---

## 🎯 Problem Statement

### Current Situation
- Many S3 buckets have versioning enabled
- When objects are deleted in versioned buckets, S3 creates "delete markers" instead of actually deleting objects
- Delete markers accumulate over time and can:
  - **Increase storage costs** (each delete marker counts as an object)
  - **Slow down bucket operations** (list operations, version queries)
  - **Make bucket management more complex**

### Evidence
- Analysis tools have been created to identify buckets with high delete marker counts
- Scripts can identify versioned buckets with delete markers ≥ threshold (e.g., 1000+)
- Object Lock buckets are automatically excluded (cannot use lifecycle rules)

---

## 💡 Proposed Solution

Enable the **"Remove expired delete markers"** lifecycle rule for versioned buckets that:
1. Have high delete marker counts
2. Don't have Object Lock enabled
3. Don't already have this rule configured

### Technical Details

**Required Configuration:**
```yaml
# For Pacman/Blob components
input:
  versioning: true
  noncurrent_expiration_days: 30  # REQUIRED - Delete markers expire when non-current versions expire
  remove_expired_object_delete_markers: true
```

```hcl
# For Terraform modules
noncurrent_expiration_days = 30  # REQUIRED

additional_custom_lifecycle_rules = [
  {
    id      = "remove-expired-delete-markers"
    enabled = true
    expiration = {
      expired_object_delete_marker = true
    }
    noncurrent_version_expiration = {
      noncurrent_days = 30  # REQUIRED
    }
  }
]
```

**Key Requirement:** `noncurrent_expiration_days` MUST be set for this to work. Delete markers are only removed when their associated non-current versions expire.

---

## 📊 Impact Analysis

### Benefits
- ✅ **Cost Reduction:** Reduces storage costs by cleaning up unnecessary delete markers
- ✅ **Performance:** Improves bucket operation performance (list, version queries)
- ✅ **Operational:** Simplifies bucket management and reduces clutter
- ✅ **Automated:** No manual intervention needed once configured

### Risks & Considerations
- ⚠️ **Non-Current Version Expiration:** Requires setting `noncurrent_expiration_days`, which means old versions will be deleted
- ⚠️ **Cannot Combine:** Cannot use `remove_expired_object_delete_markers` if `expiration_days` is set (Terraform limitation)
- ⚠️ **Object Lock Exclusion:** Buckets with Object Lock cannot use this (automatically excluded)
- ⚠️ **Gradual Cleanup:** Delete markers are removed gradually as non-current versions expire

### Affected Buckets
- Versioned buckets with high delete marker counts
- Buckets without Object Lock
- Buckets that don't already have this lifecycle rule

---

## 🔍 Analysis Tools Created

Tools have been created to identify buckets needing this change:

1. **`identify_delete_markers.py`** - Analyzes buckets and identifies those with high delete marker counts
2. **`propose_lifecycle_rule.py`** - Generates lifecycle rule proposals
3. **`IMPLEMENTATION_GUIDE.md`** - Detailed implementation guide

**Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails

---

## 📝 Implementation Plan

### Phase 1: Analysis (Ready)
- ✅ Tools created to identify buckets
- ✅ Documentation prepared
- ⏳ Run analysis on production buckets (after code freeze)

### Phase 2: Review & Approval (Pending)
- [ ] Cloud Team reviews this proposal
- [ ] Determine appropriate `noncurrent_expiration_days` value (30, 60, 90 days?)
- [ ] Identify any buckets that should be excluded
- [ ] Approve implementation approach

### Phase 3: Implementation (After Approval)
- [ ] Run analysis script to identify buckets needing changes
- [ ] Review results with Cloud Team
- [ ] Implement changes bucket-by-bucket or in batches
- [ ] Test in non-production first
- [ ] Monitor delete marker counts after deployment

### Phase 4: Validation (Post-Implementation)
- [ ] Verify lifecycle rules are applied correctly
- [ ] Monitor delete marker counts over time
- [ ] Confirm cost reduction
- [ ] Document any issues or learnings

---

## ❓ Questions for Cloud Team

1. **Retention Period:** What is the recommended `noncurrent_expiration_days` value?
   - Options: 30, 60, 90 days?
   - Should this vary by bucket type/usage?

2. **Implementation Approach:**
   - Should we implement bucket-by-bucket or all at once?
   - Any specific buckets that should be excluded?
   - Should we prioritize certain buckets (high delete marker counts)?

3. **Deployment Process:**
   - What's the process for Terraform/Pacman changes?
   - Do we need separate PRs per bucket or can we batch them?
   - Any specific review requirements?

4. **Testing:**
   - How should we test this in non-production?
   - What metrics should we monitor?
   - How do we verify the rules are working?

5. **Timeline:**
   - When can we start implementation (after code freeze)?
   - Any deadlines or priorities?

---

## 📁 Files That Will Need Changes

### Path 1: Blob Component (Pacman)
- `source/config/app/<product>/<application>/manifest.yaml`
- `infrastructure/aws/_env/service/<service>/<component>/blob_input.json`

### Path 2: Direct Terraform
- `infrastructure/aws/_env/storage/*.hcl`
- `infrastructure/aws/_env/service/*/*.hcl`
- `source/ops/s3/terraform/buckets/main.tf`

**Note:** The underlying modules already support this feature - we just need to enable it per bucket.

---

## 🔗 References

- **Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails
- **Implementation Guide:** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **AWS Documentation:** 
  - [S3 Lifecycle Management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
  - [Delete Markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeleteMarker.html)

---

## ✅ Pre-Implementation Checklist

Before implementation:
- [ ] Cloud Team approval received
- [ ] `noncurrent_expiration_days` value determined
- [ ] Buckets identified via analysis script
- [ ] Exclusions identified (Object Lock buckets, special cases)
- [ ] Implementation approach agreed upon
- [ ] Testing plan defined
- [ ] Monitoring plan in place

---

## 📅 Timeline

- **Created:** December 26, 2024
- **Code Freeze Ends:** ~January 10, 2025 (15 days)
- **Review Period:** After code freeze
- **Implementation:** After approval and code freeze completion

---

## 🙏 Next Steps

1. **Cloud Team Review:** Please review this proposal and provide feedback
2. **Answer Questions:** Address the questions above
3. **Approve Approach:** Confirm implementation approach
4. **Schedule Implementation:** Plan implementation after code freeze

---

**Contact:** [Your Name/Team]  
**Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails

