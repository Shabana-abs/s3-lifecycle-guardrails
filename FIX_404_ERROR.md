# Fix: PR Returns 404 Error

## Problem
Soji is getting a 404 error when trying to access the PR. This typically means the repository is **private** and they don't have access.

## Solution: Add Soji as a Collaborator

### Step 1: Add Soji to the Repository
1. Go to repository settings: https://github.com/Shabana-abs/s3-lifecycle-guardrails/settings
2. Click **"Collaborators"** (or **"Manage access"** in newer GitHub)
3. Click **"Add people"** or **"Invite a collaborator"**
4. Type `soji` (or their exact GitHub username)
5. Select their permission level:
   - **Read** - Can view and comment (sufficient for reviewing)
   - **Write** - Can also push changes
   - **Admin** - Full access
6. Click **"Add [username] to this repository"**

### Step 2: Share the PR Link Again
Once they're added as a collaborator, share the PR link:
```
https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
```

## Alternative: Make Repository Public (If Appropriate)

If this is a public/open-source project:
1. Go to repository settings: https://github.com/Shabana-abs/s3-lifecycle-guardrails/settings
2. Scroll to **"Danger Zone"**
3. Click **"Change visibility"** → **"Make public"**

**Note:** Only do this if the repository should be public!

## Quick Check: Verify Repository Visibility

You can check if the repo is private by:
- Looking at the repository URL - if it shows a lock icon 🔒, it's private
- Checking settings → the visibility is shown at the top

## After Adding Soji

Once soji is added as a collaborator:
1. They'll receive an email invitation
2. They need to accept the invitation
3. Then they can access the PR: https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1

---

**Repository:** https://github.com/Shabana-abs/s3-lifecycle-guardrails  
**PR:** https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
