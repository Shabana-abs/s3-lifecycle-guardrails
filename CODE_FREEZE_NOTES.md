# Code Freeze Notes - S3 Lifecycle Guardrails Implementation

**Created:** December 26, 2024  
**Code Freeze Period:** 15 days  
**Action Required After:** Contact Cloud Team after code freeze ends

---

## 📋 Summary

This project identifies versioned S3 buckets with high delete marker counts and proposes lifecycle rules to enable "Remove expired delete markers" functionality.

**Status:** ✅ Analysis tools created and ready  
**Next Step:** Implementation after code freeze (requires Cloud Team approval)

---

## 🎯 What Was Created

### Repository
- **GitHub:** https://github.com/Shabana-abs/s3-lifecycle-guardrails
- **Location:** `/Users/shabanas/dev/s3-lifecycle-guardrails`

### Tools Created

1. **`identify_delete_markers.py`**
   - Identifies versioned buckets with high delete marker counts
   - Excludes Object Lock buckets automatically
   - Outputs CSV with analysis results

2. **`propose_lifecycle_rule.py`**
   - Generates lifecycle rule proposals from analysis results
   - Outputs JSON or Terraform configuration

3. **`IMPLEMENTATION_GUIDE.md`**
   - Complete guide on which files to modify
   - Examples for both Pacman and Terraform paths
   - Step-by-step implementation instructions

---

## ⚠️ CRITICAL REQUIREMENTS

### Must-Have Settings

**For `remove_expired_object_delete_markers` to work, you MUST set:**

1. ✅ `noncurrent_expiration_days` - **REQUIRED** (e.g., 30, 60, 90 days)
2. ✅ `remove_expired_object_delete_markers: true` - **REQUIRED**

**Why:** Delete markers are only removed when their associated non-current versions expire. Without `noncurrent_expiration_days`, the rule will NOT work.

### Cannot Combine

- ❌ Cannot use `remove_expired_object_delete_markers` if `expiration_days` is set (Terraform limitation)
- ❌ Object Lock buckets are excluded (cannot use lifecycle rules for delete markers)

---

## 📁 Files That Need Modification (After Code Freeze)

### Path 1: Blob Component (Pacman) - Application Buckets

**Files to modify:**
- `source/config/app/<product>/<application>/manifest.yaml`
- `infrastructure/aws/_env/service/<service>/<component>/blob_input.json`

**What to add:**
```yaml
input:
  versioning: true
  noncurrent_expiration_days: 30  # REQUIRED!
  remove_expired_object_delete_markers: true
```

### Path 2: Direct Terraform - Infrastructure Buckets

**Files to modify:**
- `infrastructure/aws/_env/storage/*.hcl`
- `infrastructure/aws/_env/service/*/*.hcl`
- `source/ops/s3/terraform/buckets/main.tf`

**What to add:**
```hcl
noncurrent_expiration_days = 30  # REQUIRED!

additional_custom_lifecycle_rules = [
  {
    id      = "remove-expired-delete-markers"
    enabled = true
    expiration = {
      expired_object_delete_marker = true
    }
    noncurrent_version_expiration = {
      noncurrent_days = 30  # REQUIRED!
    }
  }
]
```

---

## 🔍 How to Use (After Code Freeze)

### Step 1: Run Analysis
```bash
cd /Users/shabanas/dev/s3-lifecycle-guardrails
pip install -r requirements.txt

python identify_delete_markers.py \
  --profile <aws-profile> \
  --threshold 1000 \
  --output results.csv
```

### Step 2: Generate Proposals
```bash
python propose_lifecycle_rule.py \
  --input results.csv \
  --terraform \
  --output proposals.tf
```

### Step 3: Review & Implement
- Review `proposals.tf` or `results.csv`
- Follow `IMPLEMENTATION_GUIDE.md` for specific file modifications
- Get Cloud Team approval before deploying

---

## 📝 Key Points to Discuss with Cloud Team

1. **Purpose:** Clean up accumulated delete markers in versioned S3 buckets
2. **Impact:** Reduces storage costs and improves bucket performance
3. **Requirement:** Must set `noncurrent_expiration_days` for this to work
4. **Exclusions:** Object Lock buckets are automatically excluded
5. **Testing:** Need to verify lifecycle rules are applied correctly

### Questions for Cloud Team

- [ ] What is the recommended `noncurrent_expiration_days` value? (30, 60, 90 days?)
- [ ] Should we implement this bucket-by-bucket or all at once?
- [ ] Are there any buckets that should NOT have this rule?
- [ ] What's the deployment process for Terraform/Pacman changes?
- [ ] How do we verify the rules are working after deployment?

---

## 📚 Reference Documents

1. **Implementation Guide:** `IMPLEMENTATION_GUIDE.md` - Complete file-by-file guide
2. **README:** `README.md` - Usage instructions and overview
3. **Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails

---

## 🔗 Important Links

- **Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails
- **AWS Docs:** https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html
- **Delete Markers:** https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeleteMarker.html

---

## ✅ Pre-Implementation Checklist

Before implementing after code freeze:

- [ ] Review analysis results (`results.csv`)
- [ ] Identify which buckets need changes
- [ ] Determine appropriate `noncurrent_expiration_days` value
- [ ] Check if buckets have Object Lock (excluded automatically)
- [ ] Verify buckets have versioning enabled
- [ ] Get Cloud Team approval
- [ ] Review `IMPLEMENTATION_GUIDE.md` for specific file changes
- [ ] Test in non-production environment first
- [ ] Monitor delete marker counts after deployment

---

## 🚨 Important Reminders

1. **`noncurrent_expiration_days` is REQUIRED** - Don't forget this!
2. **Cannot combine with `expiration_days`** - Terraform limitation
3. **Object Lock buckets excluded** - Manual intervention needed if cleanup required
4. **Wait for code freeze to end** - 15 days from creation date
5. **Get Cloud Team approval** - Before making any changes

---

## 📅 Timeline

- **Created:** December 26, 2024
- **Code Freeze Ends:** ~January 10, 2025 (15 days)
- **Next Action:** Contact Cloud Team after code freeze
- **Implementation:** After Cloud Team approval

---

**Note:** All tools are ready to use. Just need to wait for code freeze to end and get Cloud Team approval before implementing changes.

