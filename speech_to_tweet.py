import os
import sys
import json
import tweepy
import time
from datetime import datetime
import textwrap
from openai import OpenAI

# Twitter API credentials
consumer_key = os.environ['TWITTER_API_KEY']
consumer_secret = os.environ['TWITTER_API_SECRET_KEY']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

# OpenAI API credentials
openai_api_key = os.environ['OPENAI_API_KEY']

# Initialize OpenAI client
openai_client = OpenAI(api_key=openai_api_key)

# Initialize Tweepy client
twitter_client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Load content configuration for styling tweets
def load_content_config():
    with open('content_config.json', 'r') as f:
        return json.load(f)

# Function to transcribe audio using OpenAI Whisper API
def transcribe_audio(audio_path):
    try:
        print(f"Transcribing audio file: {audio_path}")
        
        with open(audio_path, "rb") as audio_file:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        return transcription.text
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        raise

# Function to split text into tweet-sized chunks
def split_into_tweets(text, max_length=280):
    # Simple split by sentences first
    sentences = text.replace('. ', '.\n').replace('! ', '!\n').replace('? ', '?\n').split('\n')
    
    tweets = []
    current_tweet = ""
    
    for sentence in sentences:
        # If single sentence is longer than max_length, need to split it
        if len(sentence) > max_length:
            sentence_chunks = textwrap.wrap(sentence, max_length - 5)  # -5 for ellipsis and space
            for i, chunk in enumerate(sentence_chunks):
                if i < len(sentence_chunks) - 1:
                    tweets.append(chunk + "...")
                else:
                    current_tweet = chunk
        else:
            # If adding this sentence would exceed max_length, start a new tweet
            if len(current_tweet) + len(sentence) + 1 > max_length:
                tweets.append(current_tweet)
                current_tweet = sentence
            else:
                if current_tweet:
                    current_tweet += " " + sentence
                else:
                    current_tweet = sentence
    
    # Add the last tweet if not empty
    if current_tweet:
        tweets.append(current_tweet)
    
    return tweets

# Function to apply content configuration styling to tweets
def format_tweets(tweets, config):
    brand_voice = config.get('brand_voice', '')
    values = config.get('values', [])
    
    formatted_tweets = []
    
    for tweet in tweets:
        # This is a simplified approach - in a real implementation,
        # you might use OpenAI to help reformat the tweet to match brand voice
        formatted_tweet = tweet.strip()
        
        # Add hashtags if appropriate and there's room
        if 'hashtags' in config and config['hashtags'] and len(formatted_tweet) < 260:
            # Add up to 2 relevant hashtags from config
            for hashtag in config['hashtags'][:2]:
                if len(formatted_tweet) + len(hashtag) + 1 <= 280:
                    formatted_tweet += f" {hashtag}"
        
        formatted_tweets.append(formatted_tweet)
    
    return formatted_tweets

# Function to post tweets to Twitter
def post_tweets(tweets):
    posted_tweets = []
    
    for i, tweet_text in enumerate(tweets):
        try:
            # Add thread indication for multiple tweets
            if len(tweets) > 1:
                thread_indicator = f" ({i+1}/{len(tweets)})"
                # Only add if it fits within character limit
                if len(tweet_text) + len(thread_indicator) <= 280:
                    tweet_text += thread_indicator
            
            print(f"Posting tweet: {tweet_text}")
            
            # Post the tweet
            response = twitter_client.create_tweet(text=tweet_text)
            tweet_id = response.data['id']
            
            posted_tweets.append({
                "id": tweet_id,
                "text": tweet_text,
                "posted_at": datetime.now().isoformat()
            })
            
            # Small delay between tweets to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"Error posting tweet: {str(e)}")
            # Continue posting remaining tweets even if one fails
    
    return posted_tweets

# Function to update processing history
def update_speech_history(audio_path, transcription, posted_tweets):
    history_file = 'speech_history.json'
    history = []
    
    # Load existing history if available
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Add new entry
    history.append({
        "audio_file": audio_path,
        "processed_at": datetime.now().isoformat(),
        "transcription": transcription,
        "tweets": posted_tweets
    })
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

# Main function
def main(audio_files):
    audio_file_list = audio_files.split()
    config = load_content_config()
    
    for audio_path in audio_file_list:
        try:
            # Create necessary directories
            os.makedirs('status', exist_ok=True)
            
            # Transcribe audio
            transcription = transcribe_audio(audio_path)
            print(f"Transcription: {transcription}")
            
            # Split into tweet-sized chunks
            tweet_chunks = split_into_tweets(transcription)
            print(f"Split into {len(tweet_chunks)} tweets")
            
            # Format tweets according to brand voice
            formatted_tweets = format_tweets(tweet_chunks, config)
            
            # Post tweets
            posted_tweets = post_tweets(formatted_tweets)
            
            # Update history
            update_speech_history(audio_path, transcription, posted_tweets)
            
            print(f"Successfully processed {audio_path}")
            
        except Exception as e:
            print(f"Error processing {audio_path}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("No audio files specified")