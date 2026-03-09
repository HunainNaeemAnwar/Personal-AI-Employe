# Gmail API Setup Guide

**Purpose**: Step-by-step instructions for setting up Gmail API credentials for the Gmail Watcher

**Time Required**: 15-20 minutes

## Overview

The Gmail Watcher uses OAuth2 authentication to access your Gmail inbox. This guide walks you through creating the necessary credentials in Google Cloud Console.

## Prerequisites

- Google account with Gmail
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- Basic understanding of OAuth2 (helpful but not required)

## Step 1: Create Google Cloud Project

### 1.1 Navigate to Google Cloud Console

Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)

### 1.2 Create New Project

1. Click the project dropdown at the top of the page
2. Click "New Project"
3. Enter project details:
   - **Project name**: `Personal AI Employee`
   - **Organization**: Leave as default (No organization)
   - **Location**: Leave as default
4. Click "Create"

### 1.3 Wait for Project Creation

Wait 10-30 seconds for the project to be created. You'll see a notification when it's ready.

### 1.4 Select Your Project

1. Click the project dropdown again
2. Select "Personal AI Employee" from the list

## Step 2: Enable Gmail API

### 2.1 Navigate to APIs & Services

1. Click the hamburger menu (☰) in the top-left
2. Navigate to "APIs & Services" > "Library"

### 2.2 Search for Gmail API

1. In the search box, type "Gmail API"
2. Click on "Gmail API" in the results

### 2.3 Enable the API

1. Click the blue "Enable" button
2. Wait for the API to be enabled (5-10 seconds)

You should see "API enabled" confirmation.

## Step 3: Configure OAuth Consent Screen

### 3.1 Navigate to OAuth Consent Screen

1. Click "APIs & Services" > "OAuth consent screen" in the left sidebar

### 3.2 Choose User Type

1. Select "External" (unless you have a Google Workspace account)
2. Click "Create"

### 3.3 Fill in App Information

**App information**:
- **App name**: `Personal AI Employee`
- **User support email**: Your email address
- **App logo**: (Optional - skip for now)

**App domain** (Optional - can skip):
- Leave all fields blank

**Developer contact information**:
- **Email addresses**: Your email address

Click "Save and Continue"

### 3.4 Scopes

1. Click "Add or Remove Scopes"
2. Filter for "Gmail API"
3. Select: `https://www.googleapis.com/auth/gmail.readonly`
4. Click "Update"
5. Click "Save and Continue"

### 3.5 Test Users

1. Click "Add Users"
2. Enter your Gmail address
3. Click "Add"
4. Click "Save and Continue"

### 3.6 Summary

Review the summary and click "Back to Dashboard"

## Step 4: Create OAuth Credentials

### 4.1 Navigate to Credentials

1. Click "APIs & Services" > "Credentials" in the left sidebar

### 4.2 Create Credentials

1. Click "Create Credentials" at the top
2. Select "OAuth client ID"

### 4.3 Configure OAuth Client

**Application type**:
- Select "Desktop app"

**Name**:
- Enter: `AI Employee Watcher`

Click "Create"

### 4.4 Download Credentials

1. A dialog will appear with your client ID and secret
2. Click "Download JSON"
3. Save the file (it will be named something like `client_secret_xxx.json`)

**Important**: Keep this file secure. It contains sensitive credentials.

## Step 5: Install Credentials

### 5.1 Create Credentials Directory

```bash
mkdir -p ~/.credentials
```

### 5.2 Move Credentials File

```bash
# Replace the path with your downloaded file
mv ~/Downloads/client_secret_*.json ~/.credentials/gmail-credentials.json
```

### 5.3 Verify File Location

```bash
ls -la ~/.credentials/gmail-credentials.json
```

**Expected output**: File should exist with read permissions

### 5.4 Update .env File

Edit your `.env` file:

```bash
GMAIL_CREDENTIALS_PATH=/absolute/path/to/.credentials/gmail-credentials.json
GMAIL_TOKEN_PATH=/absolute/path/to/.credentials/gmail-token.json
GMAIL_QUERY=is:unread is:important
WATCHER_TYPE=gmail
```

**Important**: Use absolute paths, not `~` or relative paths.

## Step 6: First Authentication

### 6.1 Run Watcher in Test Mode

```bash
cd ~/personal-ai-employee
source .venv/bin/activate
python main.py --test
```

### 6.2 Complete OAuth Flow

1. A browser window will open automatically
2. Sign in to your Google account (if not already signed in)
3. Review the permissions requested:
   - "Read, compose, send, and permanently delete all your email from Gmail"
   - Note: The watcher only reads emails, despite the permission text
4. Click "Continue"
5. You may see a warning "Google hasn't verified this app"
   - Click "Advanced"
   - Click "Go to Personal AI Employee (unsafe)"
   - This is safe because you created the app yourself
6. Click "Allow"

### 6.3 Verify Authentication

The browser will show "The authentication flow has completed."

In your terminal, you should see:

```
[INFO] Authentication successful
[INFO] Checking for new emails...
[INFO] Found 0 unread important emails
✅ Test complete: Found 0 new emails
```

### 6.4 Verify Token Created

```bash
ls -la ~/.credentials/gmail-token.json
```

The token file should now exist. This file will be used for future authentication (no need to re-authenticate).

## Step 7: Test with Real Email

### 7.1 Send Test Email

1. Send yourself an email with subject "Test AI Employee"
2. In Gmail, mark the email as important (star icon)

### 7.2 Run Watcher

```bash
python main.py --test
```

**Expected output**:
```
✅ Test complete: Found 1 new emails
```

### 7.3 Check Vault

```bash
ls ~/AI_Employee_Vault/Needs_Action/
```

You should see a new task file: `EMAIL_20260307T153000Z_test-ai-employee.md`

## Troubleshooting

### Error: "Credentials file not found"

**Problem**: Watcher can't find credentials file

**Solution**:
```bash
# Check file exists
ls ~/.credentials/gmail-credentials.json

# Verify path in .env is absolute
cat .env | grep GMAIL_CREDENTIALS_PATH

# Update .env with correct absolute path
```

### Error: "Invalid grant" or "Token expired"

**Problem**: OAuth token is invalid or expired

**Solution**:
```bash
# Delete old token
rm ~/.credentials/gmail-token.json

# Re-authenticate
python main.py --test
```

### Error: "Access blocked: This app's request is invalid"

**Problem**: OAuth consent screen not configured correctly

**Solution**:
1. Go back to Google Cloud Console
2. Navigate to "OAuth consent screen"
3. Verify your email is added as a test user
4. Ensure Gmail API scope is added

### Error: "The user has not granted the app..."

**Problem**: Permissions not granted during OAuth flow

**Solution**:
1. Delete token: `rm ~/.credentials/gmail-token.json`
2. Run watcher again: `python main.py --test`
3. During OAuth flow, make sure to click "Allow" for all permissions

### No Emails Detected

**Problem**: Watcher runs but doesn't find emails

**Solution**:
1. Check Gmail query in .env: `GMAIL_QUERY=is:unread is:important`
2. Verify emails match the query (unread AND important)
3. Try simpler query: `GMAIL_QUERY=is:unread`
4. Check logs: `cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json`

## Security Best Practices

### 1. Protect Credentials

```bash
# Set restrictive permissions
chmod 600 ~/.credentials/gmail-credentials.json
chmod 600 ~/.credentials/gmail-token.json
```

### 2. Never Commit Credentials

Ensure `.gitignore` includes:
```
.credentials/
*.json
.env
```

### 3. Rotate Credentials Periodically

Every 90 days:
1. Delete old credentials in Google Cloud Console
2. Create new OAuth client
3. Download new credentials
4. Replace `gmail-credentials.json`
5. Delete `gmail-token.json` and re-authenticate

### 4. Revoke Access When Not Needed

If you stop using the Gmail Watcher:
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Navigate to "Third-party apps with account access"
3. Find "Personal AI Employee"
4. Click "Remove Access"

## API Quotas and Limits

Gmail API has the following limits:

- **250 quota units per user per second**
- **1 billion quota units per day**
- Each `messages.list` call = 5 quota units
- Each `messages.get` call = 5 quota units

**Bronze tier usage**:
- Check every 2 minutes = 30 checks/hour = 720 checks/day
- ~10 emails/day = 730 API calls/day
- Total: ~3,650 quota units/day (well within limits)

## Next Steps

After Gmail Watcher is working:

1. **Customize Gmail Query**: Edit `GMAIL_QUERY` in `.env` to match your needs
   - `is:unread` - All unread emails
   - `is:unread from:client@example.com` - Unread from specific sender
   - `is:unread subject:invoice` - Unread with "invoice" in subject

2. **Test Continuous Operation**: Run watcher for 24 hours to verify stability

3. **Add Second Watcher (Silver Tier)**: Set up File System Watcher alongside Gmail

## Support

- **Gmail API Documentation**: [https://developers.google.com/gmail/api](https://developers.google.com/gmail/api)
- **OAuth2 Guide**: [https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)
- **Project Issues**: Report bugs on GitHub

**Success!** Your Gmail Watcher is now configured and ready to use.
