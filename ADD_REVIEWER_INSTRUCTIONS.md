# How to Add Soji as a Reviewer to the PR

## Option 1: Via GitHub Web Interface (Easiest)

1. Go to the PR: https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
2. On the right sidebar, find the **"Reviewers"** section
3. Click **"Add reviewers"**
4. Type `soji` in the search box
5. Select soji from the dropdown
6. Click **"Request review"**

## Option 2: Via GitHub CLI

```bash
cd /Users/shabanas/dev/s3-lifecycle-guardrails
gh pr edit 1 --add-reviewer soji
```

## Option 3: Via GitHub API

```bash
gh api repos/Shabana-abs/s3-lifecycle-guardrails/pulls/1/requested_reviewers \
  -X POST \
  -f reviewers='["soji"]'
```

## Option 4: Mention in PR Comment

You can also mention soji in a comment on the PR:

```
@soji - Could you please review this PR when you have a chance? Thanks!
```

This will notify them and they'll be able to see the PR.

---

**PR Link:** https://github.com/Shabana-abs/s3-lifecycle-guardrails/pull/1
