# S3 Lifecycle Guardrails

Tools to identify and manage S3 buckets with high delete marker counts, and propose lifecycle rules to clean them up.

> ⚠️ **IMPORTANT:** See [`CODE_FREEZE_NOTES.md`](CODE_FREEZE_NOTES.md) for important implementation notes and code freeze information.

## Overview

This repository contains scripts to:
1. **Identify versioned buckets** with high delete marker counts
2. **Exclude Object Lock buckets** (which cannot have delete markers removed via lifecycle rules)
3. **Propose lifecycle rule changes** to enable "Remove expired delete markers"

## Why This Matters

In versioned S3 buckets, when objects are deleted, S3 creates a "delete marker" instead of actually deleting the object. These delete markers accumulate over time and can:
- Increase storage costs (each delete marker counts as an object)
- Slow down bucket operations
- Make bucket management more complex

The solution is to enable a lifecycle rule that automatically removes expired delete markers. However, this cannot be done for buckets with Object Lock enabled, as Object Lock prevents deletion of objects and delete markers.

## Prerequisites

- Python 3.7+
- AWS CLI configured with appropriate profiles
- AWS credentials with permissions to:
  - `s3:ListBuckets`
  - `s3:GetBucketVersioning`
  - `s3:GetObjectLockConfiguration`
  - `s3:ListBucketVersions`
  - `s3:GetBucketLifecycleConfiguration`

## Installation

```bash
# Clone the repository
git clone https://github.com/Shabana-abs/s3-lifecycle-guardrails.git
cd s3-lifecycle-guardrails

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Step 1: Identify Buckets with High Delete Marker Counts

Run the analysis script to identify versioned buckets with high delete marker counts:

```bash
python identify_delete_markers.py --profile <aws-profile> [options]
```

**Options:**
- `--profile` (required): AWS profile to use
- `--threshold`: Threshold for 'high' delete marker count (default: 1000)
- `--max-markers`: Maximum delete markers to count per bucket (for performance)
- `--output`, `-o`: Output CSV filename
- `--region`: AWS region (optional)

**Example:**
```bash
# Analyze all buckets in a profile
python identify_delete_markers.py --profile absec-test-usa0 --threshold 1000

# Save results to CSV
python identify_delete_markers.py --profile absec-test-usa0 --threshold 1000 --output results.csv

# Limit counting for performance (stops after 10,000 markers)
python identify_delete_markers.py --profile absec-test-usa0 --threshold 1000 --max-markers 10000
```

**Output:**
The script will:
- List all buckets
- Check versioning status
- Exclude Object Lock buckets
- Count delete markers in versioned buckets
- Check if lifecycle rules already exist
- Print a summary and optionally save to CSV

### Step 2: Generate Lifecycle Rule Proposals

After identifying buckets that need attention, generate lifecycle rule proposals:

```bash
python propose_lifecycle_rule.py --input results.csv [options]
```

**Options:**
- `--input`, `-i` (required): Input CSV file from `identify_delete_markers.py`
- `--output`, `-o`: Output filename (default: `proposals.json` or `proposals.tf`)
- `--terraform`: Output as Terraform configuration instead of JSON

**Example:**
```bash
# Generate JSON proposals
python propose_lifecycle_rule.py --input results.csv --output proposals.json

# Generate Terraform configuration
python propose_lifecycle_rule.py --input results.csv --terraform --output proposals.tf
```

## Output Formats

### CSV Output (identify_delete_markers.py)

The CSV contains the following columns:
- `bucket_name`: Name of the S3 bucket
- `account_id`: AWS account ID
- `profile_name`: AWS profile used
- `is_versioned`: Whether bucket has versioning enabled
- `has_object_lock`: Whether bucket has Object Lock enabled
- `delete_marker_count`: Number of delete markers found
- `has_lifecycle_delete_marker_rule`: Whether lifecycle rule exists
- `status`: Status (`needs_attention`, `excluded`, or `ok`)

### JSON Proposals (propose_lifecycle_rule.py)

Each proposal includes:
- `bucket_name`: Bucket name
- `account_id`: AWS account ID
- `proposed_rule`: The lifecycle rule configuration
- `description`: Human-readable description
- `terraform_resource`: Terraform snippet (if using `--terraform`)

## Example Workflow

```bash
# 1. Analyze buckets
python identify_delete_markers.py \
  --profile absec-test-usa0 \
  --threshold 1000 \
  --output analysis_results.csv

# 2. Generate proposals
python propose_lifecycle_rule.py \
  --input analysis_results.csv \
  --terraform \
  --output lifecycle_proposals.tf

# 3. Review proposals.tf and apply via Terraform
```

## Understanding the Results

### Status Values

- **`needs_attention`**: Bucket is versioned, has delete markers >= threshold, and doesn't have Object Lock
- **`excluded`**: Bucket has Object Lock enabled (cannot use lifecycle rules to remove delete markers)
- **`ok`**: Bucket doesn't meet the threshold or isn't versioned

### Object Lock Exclusion

Buckets with Object Lock are automatically excluded because:
- Object Lock prevents deletion of objects and delete markers
- Lifecycle rules cannot remove delete markers in Object Lock buckets
- These buckets require manual intervention if delete markers need cleanup

## Terraform Integration

The lifecycle rule can be added to your Terraform configuration. For example, using the `infrastructure-modules` module:

```hcl
module "bucket" {
  source = "../../../provider/aws/s3/bucket"
  
  bucket = "my-bucket-name"
  
  lifecycle_rule = [
    {
      id      = "remove-expired-delete-markers"
      enabled = true
      
      expiration = {
        expired_object_delete_marker = true
      }
    }
  ]
}
```

Or using the blob module:

```yaml
# In manifest.yaml
internal-settings:
  remove_expired_object_delete_markers: true
  noncurrent_expiration_days: <number>  # Required for the rule to be effective
```

**Note:** The `expired_object_delete_marker` rule only works when combined with `noncurrent_expiration_days`. The delete markers will be removed when the non-current versions expire.

## Performance Considerations

- Counting delete markers can be slow for buckets with many versions
- Use `--max-markers` to limit counting for performance (script stops after threshold)
- The script uses pagination to handle large buckets efficiently
- Consider running during off-peak hours for large-scale analyses

## Troubleshooting

### Access Denied Errors

If you see access denied errors, ensure your AWS credentials have the required permissions:
- `s3:ListBuckets`
- `s3:GetBucketVersioning`
- `s3:GetObjectLockConfiguration`
- `s3:ListBucketVersions`
- `s3:GetBucketLifecycleConfiguration`

### Profile Not Found

Make sure your AWS profile is configured:
```bash
aws configure --profile <profile-name>
```

Or set the `AWS_PROFILE` environment variable.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for internal use.

## References

- [AWS S3 Lifecycle Management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [S3 Delete Markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeleteMarker.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)

## Important Documents

- **[CODE_FREEZE_NOTES.md](CODE_FREEZE_NOTES.md)** - ⚠️ **READ THIS FIRST** - Code freeze notes, implementation checklist, and key requirements
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Detailed guide on which files to modify for implementation

