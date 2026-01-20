# Cloud Team: S3 Delete Marker Lifecycle Rule Implementation

## ✅ Proposal Approved

**Status:** Proposal reviewed and approved by Soji Bello  
**Date:** December 30, 2024  
**Proposal PR:** https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1

## 📋 Summary

This proposal enables lifecycle rules to automatically remove expired delete markers in versioned S3 buckets. This will:
- Reduce storage costs and metadata overhead
- Improve bucket operation performance
- Simplify bucket management

## 🎯 What We Need from Cloud Team

### 1. Review the Proposal
Please review PR #1: https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1

### 2. Answer Key Questions

1. **Retention Period:** What is the recommended `noncurrent_expiration_days` value?
   - Options: 30, 60, 90 days?
   - Should this vary by bucket type/usage?

2. **Implementation Approach:**
   - Should we implement bucket-by-bucket or in batches?
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
   - When can we start implementation?
   - Any deadlines or priorities?

## 📊 Next Steps

### Phase 1: Analysis
- [ ] Run analysis script to identify buckets with high delete marker counts
- [ ] Share results with Cloud Team
- [ ] Review and prioritize buckets

### Phase 2: Implementation (After Cloud Team Approval)
- [ ] Get Cloud Team approval on retention period and approach
- [ ] Implement changes bucket-by-bucket or in batches
- [ ] Test in non-production first
- [ ] Monitor delete marker counts after deployment

## 🔗 Resources

- **Proposal PR:** https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
- **Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails
- **Implementation Guide:** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Analysis Tools:** Ready to use

## 📝 Implementation Details

### What Will Change

**For Blob Components (Pacman):**
- Add `noncurrent_expiration_days: <number>` 
- Add `remove_expired_object_delete_markers: true`

**For Direct Terraform:**
- Add lifecycle rules with `expired_object_delete_marker: true`
- Set `noncurrent_expiration_days`

### Safety Guarantees

- ✅ Does not delete current object versions
- ✅ Does not remove non-current versions before retention period
- ✅ Only removes delete markers after versions expire
- ✅ Object Lock buckets excluded
- ✅ No manual deletions; handled by S3 lifecycle
- ✅ Changes require Cloud Team review and bucket-level approval

## ⏰ Timeline

- **Status:** Ready for Cloud Team review
- **Analysis:** Ready to run
- **Implementation:** After Cloud Team approval

---

**Contact:** Ready to proceed after Cloud Team review and approval.
