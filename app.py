import io
import string
from turtle import pd
from flask import Flask, jsonify, render_template, request, redirect, send_file, send_from_directory, session, url_for, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

import numpy as np
import requests
import pandas as pd

from googleapiclient.discovery import build

import matplotlib.pyplot as plt

import base64
import matplotlib
from matplotlib import font_manager
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
import time

import os
from googleapiclient.errors import HttpError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from datasets import load_dataset

from transformers import T5ForConditionalGeneration, T5Tokenizer
import language_tool_python


summarizer = pipeline('summarization', model="sshleifer/distilbart-cnn-12-6")

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kisanjena@123'
app.config['MYSQL_DB'] = 'user_database'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

#&  Landing, SIGN UP, LOGIN UP pages Routes
@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check for existing email
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email already exists. Please use a different email address.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user details into the database
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))
    
    return render_template('login.html', show_signup=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Retrieve user details from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        cur.close()

        if user is None:
            flash('Email not found.', 'danger')
            return redirect(url_for('login'))

        # Check if the password matches
        if not bcrypt.check_password_hash(user[3], password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('login'))

        # Successful login
        session['user_id'] = user[0]
        session['user_email'] = user[2]  # Store user email in session
        flash('Login successful!', 'success')
        return redirect(url_for('landing_page'))

    return render_template('login.html', show_signup=False)

@app.route('/logout')
def logout():
    session.clear()  # Clear the session completely
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing_page'))

#& Hhandling Routes  for PAGE1(start_page),page2(Channel analysis page),summary_page,sentiment_page,title_page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST' and request.form.get('action') == 'get-started-2':
        return redirect(url_for('summary'))

    if request.method == 'POST' and request.form.get('action') == 'get-started-3':
        return redirect(url_for('page2'))
    
    if request.method == 'POST' and request.form.get('action') == 'get-started-1':
        return redirect(url_for('sentiment'))
    
    if request.method == 'POST' and request.form.get('action') == 'get-started-4':
        return redirect(url_for('titlepage'))

    return render_template('page1.html')

@app.route('/summary')
def summary():
    if 'user_id' not in session:
        flash('Please log in to access the summary page.', 'warning')
        return redirect(url_for('login'))
    return render_template('summary.html')

@app.route('/get_started')
def get_started():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))
    
@app.route('/page2')
def page2():
    if 'user_id' not in session:
        flash('Please log in to access the summary page.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('page2.html')

@app.route('/sentiment')
def sentiment():
    if 'user_id' not in session:
        flash('Please log in to access the summary page.', 'warning')
        return redirect(url_for('login'))
    return render_template('sentiment.html')

@app.route('/titlepage')
def titlepage():
    if 'user_id' not in session:
        flash('Please log in to access the summary page.', 'warning')
        return redirect(url_for('login'))
    return render_template('titlepage.html')

@app.route('/forgot-password')
def forgot_password():
    if 'user_id' not in session:
        flash('Please log in to access the summary page.', 'warning')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')
    
#& -------------------------------CODE FOR PROFILE--------------------------------------

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Access denied, user should Login', 'warning')
        return redirect(url_for('landing_page'))

    user_id = session['user_id']

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        # Update name and email in the database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (name, email, user_id))

        # Check if a new profile image is uploaded
        if 'profile_image' in request.files:
            image = request.files['profile_image']
            if image and allowed_file(image.filename):
                image_data = image.read()
                cur.execute("UPDATE users SET profile_image = %s WHERE id = %s", (image_data, user_id))

        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True})

    # Retrieve user details including the profile image
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, email, profile_image FROM users WHERE id = %s", [user_id])
    user_data = cur.fetchone()
    cur.close()

    username, email, profile_image = user_data

    # Serve the image if it exists
    image_url = None
    if profile_image:
        image_url = url_for('get_profile_image')
    else:
        image_url = url_for('static', filename='default-avatar.png')

    return render_template('profile.html', username=username, email=email, image_url=image_url)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get_profile_image')
def get_profile_image():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT profile_image FROM users WHERE id = %s", [user_id])
    profile_image = cur.fetchone()[0]
    cur.close()

    if profile_image:
        return send_file(io.BytesIO(profile_image), mimetype='image/png')  # Adjust mimetype if necessary
    else:
        return redirect(url_for('static', filename='default-avatar.png'))
    
@app.route('/res')
def res():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('res.html')


#& ----------------------------CHANNEL ANALYSIS---------------------------------
api_key = 'AIzaSyBqUeaTyMK3LsGYklFRK0VNnG7NvFabhPc'
youtube = build('youtube', 'v3', developerKey=api_key)

# Helper functions
def extract_channel_id(url):
    patterns = {
        'channel': r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/channel\/([a-zA-Z0-9_-]+)',
        'custom': r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/@([a-zA-Z0-9_-]+)',
        'playlist': r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)',
        'video': r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            if key == 'channel':
                return match.group(1)
            elif key == 'custom':
                return get_channel_id_from_custom_url(match.group(1))
            elif key == 'playlist':
                return get_channel_id_from_playlist(match.group(1))
            elif key == 'video':
                return get_channel_id_from_video(match.group(1))
    return None
def get_channel_id_from_custom_url(username):
    try:
        response = requests.get(f"https://www.youtube.com/@{username}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            channel_id_meta = soup.find('meta', {'itemprop': 'channelId'})
            if channel_id_meta and channel_id_meta['content']:
                return channel_id_meta['content']
    except Exception as e:
        print(f"Error scraping custom URL {username}: {e}")
    return None

def get_channel_id_from_playlist(playlist_id):
    try:
        response = youtube.playlists().list(part="snippet", id=playlist_id).execute()
        return response['items'][0]['snippet']['channelId'] if 'items' in response else None
    except Exception as e:
        print(f"Error fetching channel from playlist: {e}")
    return None

def get_channel_id_from_video(video_id):
    try:
        response = youtube.videos().list(part="snippet", id=video_id).execute()
        return response['items'][0]['snippet']['channelId'] if 'items' in response else None
    except Exception as e:
        print(f"Error fetching channel from video: {e}")
    return None

def get_channel_stats(channel_id):
    try:
        response = youtube.channels().list(
            part="snippet,contentDetails,statistics", id=channel_id
        ).execute()
        data = response['items'][0] if 'items' in response else None
        if data:
            return {
                'Channel_name': data['snippet']['title'],
                'Subscribers': data['statistics'].get('subscriberCount', 0),
                'Views': data['statistics'].get('viewCount', 0),
                'Total_videos': data['statistics'].get('videoCount', 0),
                'playlist_id': data['contentDetails']['relatedPlaylists'].get('uploads', None),
                'Created_date': data['snippet']['publishedAt'][:10]
            }
    except Exception as e:
        print(f"Error fetching channel stats: {e}")
    return None

def get_profile_picture(channel_id):
    try:
        response = youtube.channels().list(part="snippet", id=channel_id).execute()
        return response['items'][0]['snippet']['thumbnails']['high']['url'] if 'items' in response else None
    except Exception as e:
        print(f"Error fetching profile picture: {e}")
    return None

def get_banner_image(channel_id):
    try:
        response = youtube.channels().list(part="brandingSettings", id=channel_id).execute()
        return response['items'][0]['brandingSettings']['image']['bannerExternalUrl'] if 'items' in response else None
    except Exception as e:
        print(f"Error fetching banner image: {e}")
    return None

def get_video_ids(playlist_id):
    if not playlist_id:
        return []
    video_ids = []
    try:
        request = youtube.playlistItems().list(part="contentDetails", playlistId=playlist_id, maxResults=50).execute()
        video_ids.extend([item['contentDetails']['videoId'] for item in request['items']])
        while 'nextPageToken' in request:
            request = youtube.playlistItems().list(
                part="contentDetails", playlistId=playlist_id, maxResults=50, pageToken=request['nextPageToken']
            ).execute()
            video_ids.extend([item['contentDetails']['videoId'] for item in request['items']])
    except Exception as e:
        print(f"Error fetching video IDs: {e}")
    return video_ids

def get_video_details(video_ids):
    all_video_stats = []
    try:
        for i in range(0, len(video_ids), 50):
            request = youtube.videos().list(
                part="snippet,statistics", id=','.join(video_ids[i:i+50])
            ).execute()
            for video in request.get('items', []):
                video_stats = {
                    'Title': video['snippet']['title'],
                    'Published_date': video['snippet']['publishedAt'][:10],
                    'Views': int(video['statistics'].get('viewCount', 0)),
                    'Likes': int(video['statistics'].get('likeCount', 0)),
                    'Comments': int(video['statistics'].get('commentCount', 0)),
                    'Dislikes': 'N/A',  # Dislike count is not available
                    'Video_ID': video['id'],
                    'Thumbnail': video['snippet']['thumbnails']['default']['url']
                }
                all_video_stats.append(video_stats)
    except Exception as e:
        print(f"Error fetching video details: {e}")
    return all_video_stats

def get_videos_from_channel(channel_id):
    all_videos = []
    try:
        response = youtube.search().list(
            part="snippet", channelId=channel_id, maxResults=50, order="date", type="video"
        ).execute()
        for video in response['items']:
            video_stats = {
                'Title': video['snippet']['title'],
                'Published_date': video['snippet']['publishedAt'][:10],
                'Video_ID': video['id']['videoId'],
                'Thumbnail': video['snippet']['thumbnails']['default']['url'],
                'Views': 0,
                'Likes': 0,
                'Comments': 0,
                'Dislikes': 'N/A'
            }
            all_videos.append(video_stats)
        while 'nextPageToken' in response:
            response = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=50,
                order="date",
                pageToken=response['nextPageToken'],
                type="video"
            ).execute()
            for video in response['items']:
                video_stats = {
                    'Title': video['snippet']['title'],
                    'Published_date': video['snippet']['publishedAt'][:10],
                    'Video_ID': video['id']['videoId'],
                    'Thumbnail': video['snippet']['thumbnails']['default']['url'],
                    'Views': 0,
                    'Likes': 0,
                    'Comments': 0,
                    'Dislikes': 'N/A'
                }
                all_videos.append(video_stats)
    except Exception as e:
        print(f"Error fetching videos from channel: {e}")
    return all_videos

@app.route('/search', methods=['POST'])
def search():
    channel_url = request.form['channel_url']
    channel_id = extract_channel_id(channel_url)

    if not channel_id:
        flash('Invalid YouTube URL or unable to fetch channel ID. Please try a different URL.', 'danger')
        return redirect(url_for('link_page'))

    profile_pic = get_profile_picture(channel_id)
    banner_image = get_banner_image(channel_id)
    channel_data = get_channel_stats(channel_id)
    
    if not channel_data:
        flash('Failed to retrieve channel information. Please check the URL.', 'danger')
        return redirect(url_for('link_page'))

    video_ids = get_video_ids(channel_data.get('playlist_id')) if channel_data else []
    if not video_ids:
        videos = get_videos_from_channel(channel_id)
    else:
        videos = get_video_details(video_ids)

    # Get detailed stats for all videos if needed
    if not video_ids:
        video_ids = [video['Video_ID'] for video in videos]
        videos = get_video_details(video_ids)

    # Get top 10 videos by views
    top_videos = sorted(videos, key=lambda x: x.get('Views', 0), reverse=True)[:10]

    # Prepare data for charts
    top10_videos_data = {
        'labels': [video['Title'] for video in top_videos],
        'data': [video['Views'] for video in top_videos]
    }

    # Prepare data for number of videos per month chart
    if videos:
        video_df = pd.DataFrame(videos)
        video_df['Published_date'] = pd.to_datetime(video_df['Published_date'])
        monthly_video_counts = video_df.groupby(video_df['Published_date'].dt.to_period('M')).size()
        monthly_videos_data = {
            'labels': monthly_video_counts.index.astype(str).tolist(),
            'data': monthly_video_counts.tolist()
        }
    else:
        monthly_videos_data = {'labels': [], 'data': []}

    return render_template(
        'res.html', 
        profile_pic=profile_pic, 
        banner_image=banner_image, 
        channel_data=channel_data, 
        top10_videos_data=top10_videos_data, 
        monthly_videos_data=monthly_videos_data,
        recent_videos=videos[:5],
        top_videos=top_videos  # Pass top_videos to template
    )
#& ---------------------SUMAARY CODE----------------------------
def get_transcript(video_id):
    try:
        # Fetch transcript for the given video ID
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        result = ""
        for entry in transcript:
            result += ' ' + entry['text']
        return result
    except Exception as e:
        return str(e)

def summarize_text(text):
    num_iters = int(len(text) / 1000)
    summarized_text = []
    for i in range(num_iters + 1):
        start = i * 1000
        end = (i + 1) * 1000
        chunk = text[start:end]

        # Set max_length to ensure it's shorter than input length
        max_len = min(len(chunk) // 2, 142)
        out = summarizer(chunk, max_length=max_len, min_length=30, do_sample=False)
        summarized_text.append(out[0]['summary_text'])

    return ' '.join(summarized_text)

@app.route('/')
def index():
    return send_from_directory('templates', 'summary.html')

@app.route('/summarize', methods=['POST'])
def summarize_video():
    start_time = time.time()
    data = request.json
    video_id = data.get('video_id')
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    transcript = get_transcript(video_id)
    if 'error' in transcript.lower():
        return jsonify({"error": transcript}), 400

    summary = summarize_text(transcript)
    return jsonify({"summary": summary})

#& -------------------------Sentiment--------------------------------
# Load and prepare dataset for training
def load_and_prepare_dataset():
    # Load the dataset from Hugging Face
    dataset = load_dataset("prasadsawant7/sentiment_analysis_preprocessed_dataset", split='train')
    # Convert the dataset to a pandas DataFrame
    df = pd.DataFrame(dataset)

    # Print the column names to inspect them
    print(df.columns)

    return df

# Text cleaning function
def clean_text(text):
    if isinstance(text, str):
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    else:
        return ''  # Return empty string for None or NaN values

# Fetch comments from YouTube API
def video_comments(video_id):
    youtube = build('youtube', 'v3', developerKey='AIzaSyBwR8yST07BkRzasKzBYVRFB1g5IngYnWo')
    comments = []
    next_page_token = None
    while True:
        try:
            response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                textFormat='plainText',
                pageToken=next_page_token
            ).execute()

            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return comments

# Sentiment analysis
def analyze_youtube_video_sentiment(video_id, model, tfidf):
    comments = video_comments(video_id)

    if not comments:
        print("No comments found.")
        return []

    cleaned_comments = [clean_text(comment) for comment in comments]
    X_comments = tfidf.transform(cleaned_comments).toarray()
    predicted_sentiments = model.predict(X_comments)

    positive_percentage, negative_percentage, neutral_percentage = calculate_sentiment_percentages(predicted_sentiments)
    
    results = {
        'positive_percentage': positive_percentage,
        'negative_percentage': negative_percentage,
        'neutral_percentage': neutral_percentage,
        'positive_comments': [comments[i] for i, s in enumerate(predicted_sentiments) if s == 2][:10],
        'negative_comments': [comments[i] for i, s in enumerate(predicted_sentiments) if s == 0][:10],
        'neutral_comments': [comments[i] for i, s in enumerate(predicted_sentiments) if s == 1][:10]
    }

    return results

# Calculate sentiment percentages
def calculate_sentiment_percentages(sentiments):
    total_comments = len(sentiments)
    sentiments = np.array(sentiments)

    positive = np.sum(sentiments == 2)
    negative = np.sum(sentiments == 0)
    neutral = np.sum(sentiments == 1)

    if total_comments > 0:
        positive_percentage = (positive / total_comments) * 100
        negative_percentage = (negative / total_comments) * 100
        neutral_percentage = (neutral / total_comments) * 100
    else:
        positive_percentage = 0
        negative_percentage = 0
        neutral_percentage = 0

    return positive_percentage, negative_percentage, neutral_percentage

# Plot sentiment pie chart
def plot_sentiment_pie_chart(positive_percentage, negative_percentage, neutral_percentage, save_path):
    labels = 'Positive', 'Negative', 'Neutral'
    sizes = [positive_percentage, negative_percentage, neutral_percentage]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.1, 0, 0)  # explode the 1st slice (positive)

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title('Sentiment Distribution of YouTube Comments')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a file
    plt.savefig(save_path)
    plt.close()

# Prepare dataset and train the model
df = load_and_prepare_dataset()
df['cleaned_text'] = df['text'].apply(clean_text)

tfidf = TfidfVectorizer(max_features=2000)
X = tfidf.fit_transform(df['cleaned_text'])
y = df['labels']

X_train, X_test, y_train, y_test = train_test_split(X, df['labels'], test_size=0.3, random_state=42)
model = MultinomialNB()
model.fit(X_train, y_train)



@app.route('/analyze', methods=['POST'])
def analyze():
    video_id = request.form['video_id']
    if not video_id:
        return redirect(url_for('index'))

    # Perform sentiment analysis and generate pie chart
    results = analyze_youtube_video_sentiment(video_id, model, tfidf)

    # Save the pie chart
    pie_chart_path = os.path.join('static', 'sentiment_pie_chart.png')
    plot_sentiment_pie_chart(results['positive_percentage'], 
                             results['negative_percentage'], 
                             results['neutral_percentage'], 
                             pie_chart_path)

    return render_template('senti_result.html', video_id=video_id, results=results, pie_chart_url=pie_chart_path)


# &-------------------------------- Title Recommendation-------------------------------- 
title_model = T5ForConditionalGeneration.from_pretrained("./fine-tuned-t5")
tokenizer = T5Tokenizer.from_pretrained("./fine-tuned-t5")

# Initialize the grammar checking tool
tool = language_tool_python.LanguageTool('en-US')

def generate_title(description):
    # Refined prompt for better clarity
    input_text = f"Create a catchy and relevant YouTube title for the following description: {description}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True)

    # Generate a title with adjusted parameters
    output = title_model.generate(
        **inputs,
        max_length=50,
        top_p=0.9,
        top_k=50,
        temperature=0.7,
        num_return_sequences=1
    )

    # Decode the generated title
    title = tokenizer.decode(output[0], skip_special_tokens=True)
    return title

def check_grammar(title):
    matches = tool.check(title)
    corrected_title = language_tool_python.utils.correct(title, matches)
    return corrected_title

@app.route('/generate-title', methods=['GET', 'POST'])
def title():
    title = None
    error = None
    if request.method == 'POST':
        description = request.form.get('description')
        if description:
            try:
                generated_title = generate_title(description)
                corrected_title = check_grammar(generated_title)
                title = corrected_title
            except Exception as e:
                error = f"An error occurred: {str(e)}"
        else:
            error = "Please enter a description."

    return render_template('titlepage.html', title=title, error=error)


if __name__ == "__main__":
    app.run(debug=True, port=5001)