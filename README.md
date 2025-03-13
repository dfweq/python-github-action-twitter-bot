# AI-Powered Twitter Automation

Automate your Twitter presence with AI-generated content personalized to your brand voice.

## Overview

This project leverages GitHub Actions, OpenAI, and Twitter's API to automatically generate and post content that aligns with your personal brand. Perfect for busy professionals who want to maintain a social media presence without the daily time investment.

## Features

- **AI-Generated Content**: Uses OpenAI's GPT models to create original tweets
- **Automated Posting**: Scheduled tweets via GitHub Actions
- **Customizable Voice**: Configure your brand's tone, topics, and style
- **Hands-off Operation**: Once set up, runs autonomously
- **Post History Tracking**: Maintains a record of all published content

## Technical Architecture

```
GitHub Actions → OpenAI API → Twitter API
     ↑               ↑            ↓
     └─── Content Config ─────→ Post History
```

- **GitHub Actions**: Handles scheduling and automation
- **OpenAI API**: Generates personalized content
- **Twitter API**: Posts content to your Twitter account
- **JSON Files**: Store configuration and post history

## Setup Instructions

### Prerequisites

- Twitter Developer Account with API credentials
- OpenAI API key
- GitHub account

### Installation

1. **Fork or clone this repository**

2. **Set up GitHub Secrets**
   
   Add the following secrets to your GitHub repository:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET_KEY`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `OPENAI_API_KEY`

3. **Configure your content strategy**
   
   Edit `content_config.json` to reflect your personal brand voice, topics, and posting preferences.

4. **Enable GitHub Actions**
   
   Go to the Actions tab in your repository and enable workflows.

## Configuration Options

### Content Configuration

The `content_config.json` file controls what kind of content gets generated:

```json
{
  "brand_voice": "professional yet personable",
  "values": ["innovation", "creativity", "learning"],
  "hashtags": ["#tech", "#ai", "#innovation"],
  "avoid": "controversial topics, offensive language",
  "topics": [
    {
      "subject": "tech industry insights",
      "style": "analytical"
    },
    // Add more topics...
  ],
  "posting_frequency": {
    "times_per_week": 3,
    "optimal_days": ["Monday", "Wednesday", "Friday"],
    "optimal_time": "10:00" 
  }
}
```

### Posting Schedule

Modify `.github/workflows/openai-twitter.yml` to change the posting schedule:

```yaml
schedule:
  - cron: '0 10 * * 1,3,5'  # 10:00 UTC on Monday, Wednesday, Friday
```

## Manual Testing

To test the system locally or in GitHub Codespaces:

```bash
# Set environment variables
export TWITTER_API_KEY=your_key_here
export TWITTER_API_SECRET_KEY=your_secret_here
export TWITTER_ACCESS_TOKEN=your_token_here
export TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
export OPENAI_API_KEY=your_openai_key_here

# Run the script
python openai_twitter.py
```

## Twitter API Requirements

For this app to work correctly, your Twitter Developer App needs:

1. **Read and Write permissions** (not just Read)
2. Set as a **Web App, Automated App or Bot**
3. Valid callback URL and website URL

If you get a 403 Forbidden error, check these settings in the Twitter Developer Portal.

## Customization Ideas

- Add image generation with DALL-E
- Integrate with social media analytics
- Create topic-specific posting schedules
- Implement engagement tracking
- Add reply automation

## Troubleshooting

**403 Forbidden Errors**
- Check your Twitter API permissions (needs Read + Write)
- Regenerate access tokens after changing permissions

**Rate Limiting**
- Ensure you're not exceeding Twitter's API rate limits
- Consider reducing posting frequency

**Content Issues**
- Refine your `content_config.json` for better results
- Add more specific topic examples

## License

MIT

---

*Built with OpenAI, Tweepy, and GitHub Actions. For personal or commercial use.*
