# AWS CLI Configuration Guide

## Current Status

- AWS CLI is installed at `/Users/shabanas/bin/aws`
- AWS config directory (`~/.aws/`) does not exist yet
- Permission issues detected with cloudwatch_env virtual environment

## Setup Instructions

### Step 1: Create AWS Configuration Directory

```bash
mkdir -p ~/.aws
chmod 700 ~/.aws
```

### Step 2: Configure AWS CLI

You have two options:

#### Option A: Interactive Configuration (Recommended)

```bash
aws configure
```

This will prompt you for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., `us-east-1`)
- Default output format (e.g., `json`)

#### Option B: Manual Configuration

Create the config file:

```bash
cat > ~/.aws/config << 'EOF'
[default]
region = us-east-1
output = json

# Add additional profiles as needed
[profile absec-test-usa0]
region = us-east-1
output = json
EOF
```

Create the credentials file:

```bash
cat > ~/.aws/credentials << 'EOF'
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

# Add additional profiles as needed
[absec-test-usa0]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
EOF

chmod 600 ~/.aws/credentials
```

### Step 3: Verify Configuration

```bash
# Test default profile
aws sts get-caller-identity

# Test specific profile
aws sts get-caller-identity --profile absec-test-usa0

# List S3 buckets
aws s3 ls

# List buckets with specific profile
aws s3 ls --profile absec-test-usa0
```

## Common Profiles Used in This Codebase

Based on the codebase, common AWS profiles include:
- `absec-test-usa0` - Test environment
- Various production profiles (check your team's documentation)

## Troubleshooting

### Permission Errors

If you see permission errors with the cloudwatch_env:

1. **Use system Python AWS CLI:**
   ```bash
   /usr/local/bin/aws --version  # or wherever system AWS CLI is
   ```

2. **Install AWS CLI via Homebrew (recommended):**
   ```bash
   brew install awscli
   ```

3. **Use Python virtual environment:**
   ```bash
   python3 -m venv ~/aws-cli-env
   source ~/aws-cli-env/bin/activate
   pip install awscli
   ```

### Fix Permission Issues

If you're getting permission errors with the current AWS CLI:

```bash
# Check the AWS CLI wrapper script
cat /Users/shabanas/bin/aws

# Consider reinstalling AWS CLI
brew install awscli
# or
pip3 install --user awscli
```

### Environment Variables

You can also use environment variables instead of config files:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=absec-test-usa0  # if using profiles
```

## Using with S3 Lifecycle Guardrails Scripts

Once configured, you can use the scripts:

```bash
# With default profile
python identify_delete_markers.py --profile default --threshold 1000

# With specific profile
python identify_delete_markers.py --profile absec-test-usa0 --threshold 1000 --output results.csv
```

## Security Best Practices

1. **Never commit credentials to git**
   - `.aws/credentials` should be in `.gitignore`
   - Use environment variables or AWS SSO when possible

2. **Use AWS SSO (if available):**
   ```bash
   aws configure sso
   ```

3. **Set proper file permissions:**
   ```bash
   chmod 700 ~/.aws
   chmod 600 ~/.aws/credentials
   chmod 600 ~/.aws/config
   ```

4. **Use IAM roles instead of access keys when possible**

## Getting AWS Credentials

If you need to get AWS credentials:

1. **From AWS Console:**
   - Go to IAM → Users → Your User → Security Credentials
   - Create Access Key

2. **From AWS SSO:**
   - Contact your AWS administrator
   - Use `aws configure sso`

3. **From your team:**
   - Check team documentation or password manager
   - Ask Cloud Team for access

## Testing the Configuration

After setup, test with:

```bash
# Check your identity
aws sts get-caller-identity

# List S3 buckets
aws s3 ls

# Check specific bucket (like abnormal-security-siem-logs)
aws s3api get-bucket-location --bucket abnormal-security-siem-logs
aws s3api get-bucket-versioning --bucket abnormal-security-siem-logs
aws s3api get-bucket-lifecycle-configuration --bucket abnormal-security-siem-logs
```

## Next Steps

1. Create `~/.aws/` directory
2. Run `aws configure` or manually create config files
3. Test with `aws sts get-caller-identity`
4. Use the S3 lifecycle guardrails scripts

