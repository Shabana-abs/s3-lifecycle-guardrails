# Next Steps for Cloud Team - S3 Delete Marker Lifecycle Rule Implementation

## ✅ Proposal Approved

**Status:** Proposal has been reviewed and approved by Soji  
**PR:** https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1

## 📋 Implementation Plan

### Phase 1: Analysis (Ready to Execute)
- ✅ Analysis tools created and ready
- ✅ Documentation prepared
- ⏳ **Next:** Run analysis on production buckets to identify candidates

**Action Required:**
```bash
# Run analysis to identify buckets:
python identify_delete_markers.py \
  --profile <aws-profile> \
  --threshold 1000 \
  --output analysis_results.csv
```

### Phase 2: Cloud Team Review & Decision
- [ ] Cloud Team reviews analysis results
- [ ] Determine appropriate `noncurrent_expiration_days` value (30, 60, 90 days?)
- [ ] Identify any buckets that should be excluded
- [ ] Approve implementation approach
- [ ] Decide on batch vs. bucket-by-bucket implementation

### Phase 3: Implementation (After Approval)
- [ ] Implement changes per approved buckets
- [ ] Test in non-production first
- [ ] Deploy to production
- [ ] Monitor delete marker counts after deployment

## ❓ Questions for Cloud Team

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

## 📁 Files That Will Need Changes

### Path 1: Blob Component (Pacman)
- `source/config/app/<product>/<application>/manifest.yaml`
- `infrastructure/aws/_env/service/<service>/<component>/blob_input.json`

### Path 2: Direct Terraform
- `infrastructure/aws/_env/storage/*.hcl`
- `infrastructure/aws/_env/service/*/*.hcl`
- `source/ops/s3/terraform/buckets/main.tf`

**Note:** The underlying modules already support this feature - we just need to enable it per bucket.

## 🔗 Resources

- **Proposal PR:** https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
- **Implementation Guide:** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Analysis Tools:** Repository contains scripts to identify buckets needing changes
- **Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails

## 📅 Timeline

- **Proposal Created:** December 26, 2024
- **Soji Approved:** [Date]
- **Status:** Ready for Cloud Team review and implementation
- **Next Step:** Cloud Team review and approval
- **Implementation:** After Cloud Team approval

---

**Ready for Cloud Team review and next steps discussion.**
