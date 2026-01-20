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

## Changes
- Add `noncurrent_expiration_days` and `remove_expired_object_delete_markers: true` to blob component configurations
- Or add lifecycle rules to Terraform configurations for infrastructure buckets

## Impact
- ✅ Reduces storage costs
- ✅ Improves bucket performance
- ✅ Automated cleanup (no manual intervention)
- ⚠️ Requires setting `noncurrent_expiration_days` (old versions will be deleted)

## Analysis Tools
Analysis tools have been created to identify buckets needing this change:
- Repository: https://github.com/Shabana-abs/s3-lifecycle-guardrails
- See `IMPLEMENTATION_GUIDE.md` for detailed implementation steps

## Questions for Reviewers
1. What is the recommended `noncurrent_expiration_days` value? (30, 60, 90 days?)
2. Should we implement bucket-by-bucket or batch changes?
3. Any buckets that should be excluded?
4. What's the deployment process for Terraform/Pacman changes?

## Testing
- [ ] Run analysis script to identify buckets
- [ ] Test in non-production environment first
- [ ] Verify lifecycle rules are applied correctly
- [ ] Monitor delete marker counts after deployment

## References
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [AWS S3 Lifecycle Management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)






