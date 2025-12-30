# Where to Find AWS Credentials

## Common Sources for AWS Credentials

### 1. AWS Console (IAM) - If You Have Console Access

**Steps:**
1. Log into AWS Console: https://console.aws.amazon.com
2. Go to **IAM** → **Users** → **Your Username**
3. Click on **Security credentials** tab
4. Scroll to **Access keys** section
5. Click **Create access key**
6. Choose use case (e.g., "Command Line Interface (CLI)")
7. Download or copy the credentials immediately (you won't see the secret key again!)

**Note:** You need IAM permissions to create access keys. If you don't see this option, contact your AWS administrator.

---

### 2. AWS SSO (Single Sign-On) - Most Common for Organizations

If your organization uses AWS SSO (common at Abnormal Security):

**Steps:**
1. Contact your **Cloud Team** or **DevOps Team**
2. Ask for AWS SSO access
3. They'll provide:
   - SSO start URL (e.g., `https://your-org.awsapps.com/start`)
   - Your username/password
4. Configure AWS CLI with SSO:
   ```bash
   aws configure sso
   ```
5. Follow the prompts to authenticate

**Benefits of SSO:**
- No need to manage access keys manually
- Automatic credential rotation
- Better security
- Access to multiple AWS accounts/profiles

---

### 3. From Your Team / Cloud Team

**Ask your Cloud Team or DevOps team:**
- "How do I get AWS CLI access?"
- "Do we use AWS SSO?"
- "What's the process for getting AWS credentials?"

They might provide:
- SSO setup instructions
- Access keys (if not using SSO)
- Documentation/wiki links
- Onboarding guide

---

### 4. Password Manager / Team Documentation

Check:
- **1Password** / **LastPass** / **Bitwarden** - Look for "AWS" or "AWS CLI"
- **Team Wiki** / **Confluence** / **Notion** - Search for "AWS setup" or "AWS CLI"
- **Slack channels** - Ask in #cloud-team or #devops
- **Onboarding docs** - Check new employee documentation

---

### 5. Existing Configuration Files

Check if credentials are already configured elsewhere:

```bash
# Check for existing AWS config
cat ~/.aws/credentials 2>/dev/null
cat ~/.aws/config 2>/dev/null

# Check for environment variables
env | grep AWS

# Check for SSO configuration
cat ~/.aws/sso/cache/* 2>/dev/null
```

---

### 6. From AWS CLI Configure Command

If you have partial access, you can use:

```bash
aws configure
```

This will prompt you for credentials interactively.

---

## For Abnormal Security Specifically

Based on the codebase, here are likely options:

### Option A: AWS SSO (Most Likely)
1. **Contact Cloud Team** - They'll set up SSO access
2. Use `aws configure sso` to configure
3. Profiles like `absec-test-usa0` are likely SSO-based

### Option B: IAM Access Keys
1. **Ask Cloud Team** for IAM user creation
2. They'll provide access keys
3. Use `aws configure` to set up

### Option C: Existing Setup
1. Check if someone else has documented the process
2. Look in team Slack channels
3. Check internal documentation/wiki

---

## Quick Checklist

- [ ] Check AWS Console (if you have access)
- [ ] Contact Cloud Team / DevOps Team
- [ ] Check password manager
- [ ] Check team documentation/wiki
- [ ] Ask in team Slack channels
- [ ] Try `aws configure sso` (if SSO is available)

---

## Security Best Practices

⚠️ **Important:**
- **Never share credentials** in chat, email, or code
- **Never commit credentials** to git repositories
- **Use AWS SSO** when available (more secure)
- **Rotate credentials** regularly
- **Use IAM roles** instead of access keys when possible

---

## Next Steps After Getting Credentials

1. **If using SSO:**
   ```bash
   aws configure sso
   ```

2. **If using access keys:**
   ```bash
   aws configure
   # Enter your access key ID
   # Enter your secret access key
   # Enter region (us-east-1)
   # Enter output format (json)
   ```

3. **Test your configuration:**
   ```bash
   aws sts get-caller-identity
   aws s3 ls
   ```

---

## Need Help?

- **Cloud Team** - Primary contact for AWS access
- **DevOps Team** - Can help with setup
- **Team Lead** - May know the process
- **Internal Wiki** - Check for "AWS Setup" documentation

