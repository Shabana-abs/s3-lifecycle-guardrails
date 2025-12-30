# Email Template for Cloud Team

**Subject:** Proposal: Enable "Remove Expired Delete Markers" Lifecycle Rule for Versioned S3 Buckets

---

Hi Cloud Team,

I'm proposing to enable lifecycle rules to automatically remove expired delete markers in versioned S3 buckets. This will help reduce storage costs and improve bucket performance.

## The Problem
Versioned S3 buckets accumulate delete markers over time when objects are deleted. These delete markers:
- Increase storage costs (each counts as an object)
- Slow down bucket operations
- Make management more complex

## The Solution
Enable the "Remove expired delete markers" lifecycle rule for versioned buckets with high delete marker counts (excluding Object Lock buckets).

**Key Requirement:** This requires setting `noncurrent_expiration_days` because delete markers are only removed when their associated non-current versions expire.

## What I've Prepared
1. **Analysis Tools:** Scripts to identify buckets with high delete marker counts
2. **Implementation Guide:** Detailed guide on which files need changes
3. **Proposal Document:** Complete proposal with impact analysis

**Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails

## Questions
1. What's the recommended `noncurrent_expiration_days` value? (30, 60, 90 days?)
2. Should we implement bucket-by-bucket or batch changes?
3. Any buckets that should be excluded?
4. What's the deployment process for Terraform/Pacman changes?

## Next Steps
- Review the proposal: See `PR_PROPOSAL.md` in the repository
- After code freeze ends (~Jan 10), I can run the analysis and share results
- Then we can discuss implementation approach

Please let me know if you'd like to discuss this further or if you have any questions.

Thanks!

[Your Name]

---

**Attachments/Links:**
- Repository: https://github.com/Shabana-abs/s3-lifecycle-guardrails
- PR Proposal: [PR_PROPOSAL.md](PR_PROPOSAL.md)
- Implementation Guide: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)

