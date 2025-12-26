# Implementation Guide: Enabling "Remove Expired Delete Markers" Lifecycle Rule

This guide explains which files need to be modified to implement the lifecycle rule changes identified by the analysis scripts.

## Overview

There are **two main paths** for configuring S3 buckets in this codebase:

1. **Blob Component (Pacman)** - Used for application buckets via manifest.yaml files
2. **Direct Terraform** - Used for infrastructure buckets via .hcl or blob_input.json files

## Path 1: Blob Component (Pacman) - Application Buckets

### Files to Modify

#### Option A: Application Manifest Files (Recommended)
**Location:** `source/config/app/<product>/<application>/manifest.yaml`

**Example:**
```yaml
components:
  my-bucket:
    component: blob
    input:
      versioning: true
      # Add these settings:
      noncurrent_expiration_days: 30  # Required for delete marker removal to work
      remove_expired_object_delete_markers: true
```

**Files to modify:**
- `source/config/app/*/manifest.yaml` - Add lifecycle settings to blob components

#### Option B: Blob Input JSON Files (If using Terragrunt)
**Location:** `infrastructure/aws/_env/service/<service>/<component>/blob_input.json`

**Example:**
```json
{
  "input": {
    "versioning": true,
    "noncurrent_expiration_days": 30,
    "remove_expired_object_delete_markers": true
  }
}
```

**Files to modify:**
- `infrastructure/aws/_env/service/*/blob_input.json` - Add lifecycle settings

**Note:** The blob component already supports `remove_expired_object_delete_markers` (see `source/config/component/blob/manifest.yaml` lines 119-122). You just need to set it in your bucket configuration.

### How It Works

1. Pacman reads manifest.yaml or blob_input.json
2. Processes through `infrastructure-modules/modules/application/aws/blob/main.tf`
3. Translates to Terraform via the blob module
4. The setting is already supported - just needs to be enabled per bucket

---

## Path 2: Direct Terraform - Infrastructure Buckets

### Files to Modify

#### Option A: Terragrunt HCL Files
**Location:** `infrastructure/aws/_env/storage/*.hcl` or `infrastructure/aws/_env/service/*/*.hcl`

**Example:**
```hcl
terraform {
  source = "git::https://github.com/.../modules/storage/absec/aws/s3.git?ref=..."
}

inputs = {
  bucket_name = "my-bucket"
  versioning  = true
  
  # Add lifecycle rule via additional_custom_lifecycle_rules
  additional_custom_lifecycle_rules = [
    {
      id      = "remove-expired-delete-markers"
      enabled  = true
      expiration = {
        expired_object_delete_marker = true
      }
      # Note: This only works with noncurrent_expiration_days
      noncurrent_version_expiration = {
        noncurrent_days = 30
      }
    }
  ]
  
  # OR use expiration_days (but this requires noncurrent_expiration_days too)
  expiration_days = 0  # This is already set in the "standard" rule when expiration_days > 0
  noncurrent_expiration_days = 30
}
```

**Files to modify:**
- `infrastructure/aws/_env/storage/*.hcl`
- `infrastructure/aws/_env/service/*/*.hcl` - Any S3 bucket configurations

#### Option B: Direct Terraform Module Calls
**Location:** `source/ops/s3/terraform/buckets/main.tf` or similar

**Example:**
```hcl
module "my_bucket" {
  source = "../../modules/bucket"
  
  name     = "my-bucket"
  versioning = true
  
  # Add custom lifecycle rule
  life_cycle_rules = [
    {
      id      = "remove-expired-delete-markers"
      enabled  = true
      expiration = {
        days                         = null
        noncurrent_days             = 30
        expired_object_delete_marker = true
      }
    }
  ]
}
```

**Files to modify:**
- `source/ops/s3/terraform/buckets/main.tf` - Direct bucket definitions

---

## Key Implementation Details

### Important Notes

1. **`expired_object_delete_marker` requires `noncurrent_expiration_days`**
   - Delete markers are only removed when non-current versions expire
   - You MUST set `noncurrent_expiration_days` for this to work
   - See AWS docs: delete markers are removed when their associated non-current versions expire

2. **Cannot combine with `expiration_days`**
   - If `expiration_days` is set, you cannot use `remove_expired_object_delete_markers` in blob manifests
   - This is a Terraform limitation mentioned in the blob manifest comments

3. **Object Lock Buckets**
   - Buckets with Object Lock CANNOT have delete markers removed via lifecycle rules
   - These are automatically excluded by the analysis script
   - Manual intervention required if cleanup is needed

### Module Support

The following modules already support this feature:

✅ **`infrastructure-modules/modules/storage/absec/aws/s3`**
   - Supports `expired_object_delete_marker` in expiration block (line 49, 81)
   - Used via `expiration_days` variable

✅ **`infrastructure-modules/modules/application/aws/blob`**
   - Supports `remove_expired_object_delete_markers` variable
   - Translates to Terraform lifecycle rules

✅ **`source/ops/s3/terraform/modules/bucket`**
   - Supports `expired_object_delete_marker` in lifecycle rules (line 37)
   - Can be configured via `life_cycle_rules` variable

---

## Step-by-Step Implementation Process

### Step 1: Run Analysis
```bash
python identify_delete_markers.py --profile <profile> --threshold 1000 --output results.csv
```

### Step 2: Generate Proposals
```bash
python propose_lifecycle_rule.py --input results.csv --terraform --output proposals.tf
```

### Step 3: Review Proposals
Review the generated proposals to understand which buckets need changes.

### Step 4: Implement Changes

**For Blob Components (Pacman):**
1. Find the bucket's manifest file: `source/config/app/<product>/<app>/manifest.yaml`
2. Locate the blob component definition
3. Add:
   ```yaml
   input:
     versioning: true
     noncurrent_expiration_days: <number>  # e.g., 30
     remove_expired_object_delete_markers: true
   ```

**For Direct Terraform:**
1. Find the bucket's configuration file (`.hcl` or `main.tf`)
2. Add lifecycle rule configuration (see examples above)
3. Ensure `noncurrent_expiration_days` is set

### Step 5: Deploy
- For Pacman: Deploy via normal Pacman workflow
- For Terraform: Run `terragrunt apply` or `terraform apply`

---

## Example: Complete Implementation

### Example 1: Blob Component (manifest.yaml)
```yaml
components:
  data-store:
    component: blob
    input:
      versioning: true
      noncurrent_expiration_days: 30
      remove_expired_object_delete_markers: true
      # Other settings...
```

### Example 2: Terragrunt HCL
```hcl
inputs = {
  bucket_name              = "my-data-bucket"
  versioning               = true
  noncurrent_expiration_days = 30
  expiration_days          = 0  # Must be 0 or unset
  
  additional_custom_lifecycle_rules = [
    {
      id      = "remove-expired-delete-markers"
      enabled  = true
      expiration = {
        expired_object_delete_marker = true
      }
      noncurrent_version_expiration = {
        noncurrent_days = 30
      }
    }
  ]
}
```

### Example 3: Direct Terraform Module
```hcl
module "bucket" {
  source = "../../modules/bucket"
  
  name      = "my-bucket"
  versioning = true
  
  life_cycle_rules = [
    {
      id      = "remove-expired-delete-markers"
      enabled  = true
      expiration = {
        days                         = null
        noncurrent_days             = 30
        expired_object_delete_marker = true
      }
    }
  ]
}
```

---

## Files Summary

### Files That May Need Modification:

1. **Application Manifests:**
   - `source/config/app/*/manifest.yaml` - Add lifecycle settings to blob components

2. **Blob Input JSON:**
   - `infrastructure/aws/_env/service/*/blob_input.json` - Add lifecycle settings

3. **Terragrunt Configs:**
   - `infrastructure/aws/_env/storage/*.hcl` - Add lifecycle rules
   - `infrastructure/aws/_env/service/*/*.hcl` - Add lifecycle rules

4. **Direct Terraform:**
   - `source/ops/s3/terraform/buckets/main.tf` - Add lifecycle rules to bucket modules

### Files That DON'T Need Modification (Already Support This):

- ✅ `infrastructure-modules/modules/storage/absec/aws/s3/main.tf` - Already supports it
- ✅ `infrastructure-modules/modules/application/aws/blob/main.tf` - Already supports it
- ✅ `infrastructure-modules/modules/provider/aws/s3/bucket/main.tf` - Already supports it
- ✅ `source/config/component/blob/manifest.yaml` - Already defines the setting
- ✅ `source/ops/s3/terraform/modules/bucket/main.tf` - Already supports it

---

## Testing

After implementation:

1. Verify lifecycle rule is applied:
   ```bash
   aws s3api get-bucket-lifecycle-configuration --bucket <bucket-name>
   ```

2. Check that `ExpiredObjectDeleteMarker` is set to `true` in the rule

3. Monitor delete marker counts over time to confirm cleanup

---

## References

- AWS Documentation: [S3 Lifecycle Management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- AWS Documentation: [Delete Markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeleteMarker.html)
- Component Manifest: `source/config/component/blob/manifest.yaml`
- Terraform Module: `infrastructure-modules/modules/storage/absec/aws/s3/main.tf`

