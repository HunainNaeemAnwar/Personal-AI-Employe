# LinkedIn API Setup Guide

This guide covers the setup and configuration of LinkedIn integration for Silver tier.

## Prerequisites

- **LinkedIn Account**: Personal or company LinkedIn account
- **Python 3.13+**: Already installed from Bronze tier
- **LinkedIn API Credentials**: OAuth2 credentials (optional, can use Selenium fallback)

## Authentication Methods

LinkedIn Watcher supports two authentication methods:

1. **LinkedIn API** (Recommended): Official API with OAuth2
2. **Selenium Fallback**: Web scraping when API unavailable

## Method 1: LinkedIn API (Recommended)

### Step 1: Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click "Create App"
3. Fill in app details:
   - **App name**: Personal AI Employee
   - **LinkedIn Page**: Your company page (or create one)
   - **App logo**: Upload a logo
   - **Legal agreement**: Accept terms
4. Click "Create app"

### Step 2: Configure OAuth2 Settings

1. In your app dashboard, go to "Auth" tab
2. Add redirect URLs:
   ```
   http://localhost:8080/callback
   ```
3. Note your credentials:
   - **Client ID**: Copy this
   - **Client Secret**: Copy this

### Step 3: Request API Access

1. Go to "Products" tab
2. Request access to:
   - **Sign In with LinkedIn**: For authentication
   - **Share on LinkedIn**: For posting updates
   - **Messaging API**: For message monitoring (requires approval)

**Note**: Messaging API access requires LinkedIn approval and may take several days.

### Step 4: Configure Environment Variables

Add to your `.env` file:

```env
# LinkedIn API Configuration
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_ACCESS_TOKEN=your_access_token  # Optional, generated after OAuth flow
LINKEDIN_POLLING_INTERVAL=300  # 5 minutes
LINKEDIN_RATE_LIMIT_REQUESTS=100  # requests per hour
LINKEDIN_RATE_LIMIT_WINDOW=3600  # 1 hour
```

### Step 5: Test LinkedIn API Connection

```bash
python -c "from linkedin_api import Linkedin; api = Linkedin('your_email@example.com', 'your_password'); print('Connected:', api.get_profile())"
```

## Method 2: Selenium Fallback

If LinkedIn API is unavailable or you don't have API access, the watcher automatically falls back to Selenium web scraping.

### Step 1: Install Chrome/Chromium

**Linux:**
```bash
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver
```

**macOS:**
```bash
brew install --cask google-chrome
brew install chromedriver
```

**Windows:**
Download and install [Google Chrome](https://www.google.com/chrome/)

### Step 2: Configure Selenium

Selenium fallback uses your LinkedIn username and password to log in via browser automation.

**Environment variables (same as API method):**
```env
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

### Step 3: Test Selenium Fallback

```bash
python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.get('https://www.linkedin.com'); print('Selenium working')"
```

## LinkedIn Watcher Configuration

### Enable LinkedIn Watcher in Orchestrator

Update `.env` to include LinkedIn in watcher list:

```env
# Orchestrator Configuration
ORCHESTRATOR_WATCHERS=gmail,filesystem,linkedin
```

### LinkedIn Watcher Settings

```env
# LinkedIn Watcher Configuration
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_ACCESS_TOKEN=  # Optional, leave empty for password auth
LINKEDIN_POLLING_INTERVAL=300  # Check every 5 minutes
LINKEDIN_RATE_LIMIT_REQUESTS=100  # Max 100 requests per hour
LINKEDIN_RATE_LIMIT_WINDOW=3600  # 1 hour window
```

## Testing LinkedIn Integration

### Test Message Monitoring

1. Send yourself a LinkedIn message from another account
2. Wait 5 minutes (polling interval)
3. Check `/Needs_Action` for new task file:
   ```
   LINKEDIN_MSG_20260309T143000Z_John-Doe.md
   ```

### Test LinkedIn Posting

Use the LinkedIn posting skill:

```bash
claude "Create a LinkedIn post about our new AI automation service"
```

The skill will generate a post following best practices. Review and approve before posting.

## Rate Limits and Quotas

### LinkedIn API Limits

- **Free tier**: 100 requests/hour
- **Messaging API**: Requires approval, limited to 25 messages/day
- **Share API**: 100 posts/day

### Best Practices

1. **Polling interval**: 5 minutes minimum (300 seconds)
2. **Batch operations**: Check multiple messages in single API call
3. **Cache results**: Use StateManager to avoid duplicate checks
4. **Respect limits**: Watcher automatically handles rate limiting

## Troubleshooting

### Error: "LinkedIn API authentication failed"

**Solution 1**: Check credentials in `.env`
```bash
# Verify credentials
echo $LINKEDIN_USERNAME
echo $LINKEDIN_PASSWORD
```

**Solution 2**: LinkedIn may have blocked API access. Use Selenium fallback:
```env
# Watcher will automatically fall back to Selenium
```

### Error: "Rate limit exceeded"

**Solution**: Wait for rate limit window to reset (1 hour). The watcher automatically waits and retries.

### Error: "Messaging API access denied"

**Solution**: Messaging API requires LinkedIn approval. Options:
1. Apply for API access (may take days/weeks)
2. Use Selenium fallback for message monitoring
3. Manually check LinkedIn messages

### Error: "Selenium ChromeDriver not found"

**Solution**: Install ChromeDriver:
```bash
# Linux
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Windows
# Download from https://chromedriver.chromium.org/
```

### Error: "LinkedIn login failed (Selenium)"

**Solution**: LinkedIn may have CAPTCHA or security checks. Options:
1. Log in manually once to verify account
2. Use LinkedIn API instead of Selenium
3. Disable two-factor authentication temporarily

## Security Considerations

1. **Credentials**: Store in `.env` file (excluded from git)
2. **Access tokens**: Rotate regularly (every 60 days)
3. **Rate limiting**: Prevents account suspension
4. **Selenium**: Runs in headless mode (no visible browser)
5. **Logging**: No passwords logged (only success/failure)

## LinkedIn Posting Best Practices

### Content Guidelines

1. **Professional tone**: LinkedIn is a professional network
2. **Value-driven**: Share insights, not just promotions
3. **Engagement**: Ask questions, encourage comments
4. **Consistency**: Post 2-3x per week minimum
5. **Timing**: Tuesday-Thursday, 8-10 AM or 12-2 PM

### Posting Workflow

1. **Generate post**: Use LinkedIn posting skill
2. **Review content**: Check for tone, accuracy, compliance
3. **Approve**: Move to `/Approved` folder
4. **Post**: Watcher posts automatically or via manual trigger
5. **Track metrics**: Monitor engagement in LinkedIn analytics

### Performance Metrics

Track these metrics for each post:
- **Impressions**: Views
- **Engagement rate**: (Likes + Comments + Shares) / Impressions
- **Comments**: Most valuable for algorithm
- **Shares**: Extends reach
- **Profile views**: Indicates interest

**Target metrics:**
- Engagement rate: >2% good, >5% excellent
- Comments: 10+ per post
- Shares: 5+ indicates high-value content

## Integration with Other Features

### Email + LinkedIn Workflow

1. Receive client inquiry via email (Gmail watcher)
2. Draft response (Claude)
3. Send email (Email MCP server)
4. Create LinkedIn post about service (LinkedIn posting skill)
5. Post to LinkedIn (LinkedIn watcher)

### Approval Workflow

High-stakes LinkedIn posts require approval:
1. Post generated by skill
2. Moved to `/Pending_Approval`
3. User reviews and approves
4. Posted to LinkedIn
5. Logged to `/Logs/linkedin_posts.log`

## Next Steps

After setting up LinkedIn integration:

1. **Test message monitoring**: Send test message
2. **Create first post**: Use LinkedIn posting skill
3. **Monitor engagement**: Track metrics
4. **Adjust strategy**: Refine based on performance
5. **Scale posting**: Increase frequency as engagement grows

## References

- [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [LinkedIn Marketing Best Practices](https://business.linkedin.com/marketing-solutions/best-practices)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
