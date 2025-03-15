from http.server import BaseHTTPRequestHandler
import os
import json
import tempfile
import uuid
import tweepy
from openai import OpenAI
import textwrap

# Initialize clients
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# In-memory job storage (in a production app, use a database)
jobs = {}

def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

def split_into_tweets(text, max_length=280):
    # Simple split by sentences
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

def post_tweets(tweets):
    # Twitter API credentials
    consumer_key = os.environ.get("TWITTER_API_KEY")
    consumer_secret = os.environ.get("TWITTER_API_SECRET_KEY")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    
    # Initialize Twitter client
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    posted_tweets = []
    
    for i, tweet_text in enumerate(tweets):
        # Add thread indication for multiple tweets
        if len(tweets) > 1:
            thread_indicator = f" ({i+1}/{len(tweets)})"
            # Only add if it fits within character limit
            if len(tweet_text) + len(thread_indicator) <= 280:
                tweet_text += thread_indicator
        
        # Post the tweet
        response = client.create_tweet(text=tweet_text)
        posted_tweets.append({
            "id": str(response.data['id']),
            "text": tweet_text
        })
    
    return posted_tweets

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Generate a job ID
            job_id = str(uuid.uuid4())
            
            # Get content length to read the request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            
            # Parse multipart form data
            boundary = self.headers['Content-Type'].split('=')[1].encode()
            parts = body.split(boundary)
            
            audio_part = None
            for part in parts:
                if b'Content-Disposition: form-data; name="audio"' in part:
                    audio_part = part
                    break
            
            if not audio_part:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No audio file found"}).encode())
                return
            
            # Extract the audio data
            audio_data_start = audio_part.find(b'\r\n\r\n') + 4
            audio_data = audio_part[audio_data_start:]
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp:
                temp.write(audio_data)
                audio_file_path = temp.name
            
            # Store job info
            jobs[job_id] = {
                "status": "processing",
                "audio_path": audio_file_path
            }
            
            # Process in the background (in a real app, use a worker)
            try:
                # Transcribe audio
                transcription = transcribe_audio(audio_file_path)
                
                # Split into tweets
                tweets = split_into_tweets(transcription)
                
                # Post tweets
                posted_tweets = post_tweets(tweets)
                
                # Update job status
                jobs[job_id] = {
                    "status": "completed",
                    "transcription": transcription,
                    "tweets": posted_tweets
                }
            except Exception as e:
                jobs[job_id] = {
                    "status": "failed",
                    "error": str(e)
                }
                
            # Clean up temporary file
            os.unlink(audio_file_path)
            
            # Return success response with job ID
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"jobId": job_id}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()