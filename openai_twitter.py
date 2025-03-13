import os
import json
import random
import tweepy
from openai import OpenAI

# Twitter API credentials
consumer_key = os.environ['TWITTER_API_KEY']
consumer_secret = os.environ['TWITTER_API_SECRET_KEY']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

# OpenAI API credentials
openai_api_key = os.environ['OPENAI_API_KEY']

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize Tweepy client
twitter_client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Load content configuration
def load_content_config():
    with open('content_config.json', 'r') as f:
        return json.load(f)

# Generate post content using OpenAI
def generate_content(config):
    # Choose a random topic/template from our configuration
    topic = random.choice(config['topics'])
    
    # Create a prompt for OpenAI
    prompt = f"""Generate a Twitter post about {topic['subject']} with the following characteristics:
    - Tone: {config['brand_voice']}
    - Style: {topic['style']}
    - Length: Keep it under 280 characters
    - Include these hashtags if relevant: {', '.join(config['hashtags'])}
    - Avoid: {config['avoid']}
    
    The post should reflect personal brand values: {', '.join(config['values'])}
    """
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are a social media expert who creates engaging Twitter content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    
    # Extract the generated content
    content = response.choices[0].message.content.strip()
    
    # Ensure we're within Twitter's character limit
    if len(content) > 280:
        content = content[:277] + "..."
    
    return content

# Track post history
def update_post_history(content):
    history = []
    if os.path.exists('post_history.json'):
        with open('post_history.json', 'r') as f:
            history = json.load(f)
    
    # Add current post with timestamp
    from datetime import datetime
    history.append({
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "posted": True
    })
    
    # Save history
    with open('post_history.json', 'w') as f:
        json.dump(history, f, indent=2)

# Main function
def main():
    # Load configuration
    config = load_content_config()
    
    # Generate content
    content = generate_content(config)
    print(f"Generated content: {content}")
    
    # Post to Twitter
    response = twitter_client.create_tweet(text=content)
    print(f"Tweet posted! ID: {response.data['id']}")
    
    # Update history
    update_post_history(content)

if __name__ == "__main__":
    main()