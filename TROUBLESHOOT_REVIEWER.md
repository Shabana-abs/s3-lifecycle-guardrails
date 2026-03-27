# Troubleshooting: Unable to Add Soji as Reviewer

## Common Issues & Solutions

### Issue 1: Username Might Be Different
Try these variations:
- `soji` (lowercase)
- `Soji` (capitalized)
- Full GitHub username (e.g., `soji-abs` or similar)
- Check their GitHub profile for exact username

### Issue 2: PR is Draft
If the PR is still in draft mode:
1. Go to the PR: https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
2. Click "Ready for review" button (top right)
3. Then try adding reviewers

### Issue 3: Permission Issues
If you don't have permission to add reviewers:
- **Solution:** Mention them in a comment instead (see below)

### Issue 4: They're Not a Collaborator
If soji isn't a collaborator on the repository:
- They can still see the PR if you share the link
- They can comment and review
- You might need to add them as a collaborator first

## Alternative Solutions

### Option 1: Mention in PR Comment (Works Always)
Go to the PR and add a comment:

```
@soji - Could you please review this PR when you have a chance? 

PR: https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1

Thanks!
```

This will:
- Notify soji
- Give them access to see the PR
- Allow them to review

### Option 2: Share PR Link Directly
Send soji the PR link:
```
https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
```

They can:
- View the PR
- Add themselves as a reviewer (if they have permission)
- Comment and review

### Option 3: Add as Collaborator First
1. Go to repository settings: https://github.com/Shabana-abs/s3-lifecycle-guardrails/settings
2. Click "Collaborators" (or "Manage access")
3. Add soji as a collaborator
4. Then add them as a reviewer

### Option 4: Use GitHub Web Interface
1. Go to: https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
2. Scroll to right sidebar → "Reviewers" section
3. Click "Add reviewers"
4. Type their exact GitHub username
5. If it doesn't appear, they might need to be added as collaborator first

## Quick Fix: Comment Method (Recommended)

**Easiest solution:** Just add a comment on the PR mentioning @soji. This works regardless of permissions and will notify them.

---

**PR Link:** https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
