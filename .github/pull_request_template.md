# Enable "Remove Expired Delete Markers" Lifecycle Rule for Versioned S3 Buckets

## Problem
Versioned S3 buckets accumulate delete markers over time, which:
- Increase storage costs (each delete marker counts as an object)
- Slow down bucket operations (list, version queries)
- Make bucket management more complex

## Solution
Enable lifecycle rules to automatically remove expired delete markers for versioned buckets that:
- Have high delete marker counts
- Don't have Object Lock enabled
- Don't already have this rule configured

## Technical Details

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

**Important Note:** While S3 supports removing expired delete markers independently, this rule is most effective when paired with a non-current version expiration policy.

Without expiring non-current versions, delete markers may persist indefinitely. This proposal therefore recommends configuring `noncurrent_expiration_days` alongside delete marker cleanup to ensure predictable behavior.

## Safety Guarantees

- ✅ This rule does not delete current object versions
- ✅ This rule does not remove non-current versions before the configured retention period
- ✅ This rule only removes delete markers after associated object versions have expired
- ✅ Buckets with Object Lock are explicitly excluded
- ✅ No manual deletions are performed; cleanup is handled entirely by S3 lifecycle

## Impact Analysis

### Benefits
- ✅ **Cost & Metadata Reduction:** Reduces object count, metadata overhead, and associated storage/listing costs
- ✅ **Performance:** Improves bucket operation performance (list, version queries)
- ✅ **Operational:** Simplifies bucket management and reduces clutter
- ✅ **Automated:** No manual intervention needed once configured

**Note:** Delete marker cleanup occurs gradually as lifecycle rules run and eligible markers expire; no bulk deletions occur.

### Risks & Considerations
- ⚠️ **Non-Current Version Retention:** This proposal introduces a defined retention window for non-current object versions. The retention duration (e.g., 30 / 60 / 90 days) should be reviewed and approved per bucket class.
- ⚠️ **Terraform Constraint:** In Terraform, `expired_object_delete_marker` cannot be defined in the same lifecycle rule as `expiration.days`. This proposal uses a dedicated lifecycle rule to avoid configuration conflicts.
- ⚠️ **Object Lock Exclusion:** Buckets with Object Lock cannot use this (automatically excluded)
- ⚠️ **Gradual Cleanup:** Delete marker cleanup occurs gradually as lifecycle rules run and eligible markers expire; no bulk deletions occur.

## Analysis Tools Created

Tools have been created to identify buckets needing this change:
- `identify_delete_markers.py` - Analyzes buckets and identifies those with high delete marker counts
- `propose_lifecycle_rule.py` - Generates lifecycle rule proposals
- `IMPLEMENTATION_GUIDE.md` - Detailed implementation guide

## Implementation Plan

### Phase 1: Analysis (Ready)
- ✅ Tools created to identify buckets
- ✅ Documentation prepared
- ⏳ Run analysis on production buckets (after code freeze)

### Phase 2: Review & Approval (Pending)
- [ ] Cloud Team reviews this proposal
- [ ] Determine appropriate `noncurrent_expiration_days` value (30, 60, 90 days?)
- [ ] Identify any buckets that should be excluded
- [ ] Approve implementation approach
- [ ] **Changes will not be applied org-wide without Cloud review and explicit bucket-level approval**

### Phase 3: Implementation (After Approval)
- [ ] Run analysis script to identify buckets needing changes
- [ ] Review results with Cloud Team
- [ ] Implement changes bucket-by-bucket or in batches
- [ ] Test in non-production first
- [ ] Monitor delete marker counts after deployment

## Questions for Cloud Team

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

## Files That Will Need Changes

### Path 1: Blob Component (Pacman)
- `source/config/app/<product>/<application>/manifest.yaml`
- `infrastructure/aws/_env/service/<service>/<component>/blob_input.json`

### Path 2: Direct Terraform
- `infrastructure/aws/_env/storage/*.hcl`
- `infrastructure/aws/_env/service/*/*.hcl`
- `source/ops/s3/terraform/buckets/main.tf`

**Note:** The underlying modules already support this feature - we just need to enable it per bucket.

## References

- **Implementation Guide:** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **AWS Documentation:** 
  - [S3 Lifecycle Management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
  - [Delete Markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeleteMarker.html)

## Pre-Implementation Checklist

- [ ] Cloud Team approval received
- [ ] `noncurrent_expiration_days` value determined
- [ ] Buckets identified via analysis script
- [ ] Exclusions identified (Object Lock buckets, special cases)
- [ ] Implementation approach agreed upon
- [ ] Testing plan defined
- [ ] Monitoring plan in place

## Timeline

- **Created:** December 26, 2024
- **Code Freeze Ends:** ~January 10, 2025 (15 days)
- **Review Period:** After code freeze
- **Implementation:** After approval and code freeze completion




