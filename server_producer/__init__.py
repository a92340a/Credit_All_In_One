import os
import json
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter

from flask import Flask, request, render_template
from flask_socketio import SocketIO
from flask_sqlalchemy import Model, SQLAlchemy
from google.cloud.pubsublite.cloudpubsub import PublisherClient
from google.cloud.pubsublite.types import MessageMetadata

import plotly as py
import plotly.graph_objects as go
from io import BytesIO
from base64 import b64encode

from server_producer.models.hot_cards_model import fetch_all_banks, fetch_cards_ranking, \
    fetch_total_banks_and_cards, fetch_latest_cards
from server_producer.models.community_analysis_model import fetch_ptt_title_splitted, \
    fetch_ptt_article_scores, fetch_ptt_popular_articles
from server_producer.models.chat_model import fetch_latest_chats
import my_logger 
load_dotenv()


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('producer')
dev_logger.console_handler()
dev_logger.file_handler(today)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('KEY')
socketio = SocketIO(app, cors_allowed_origins="*") 


@app.route('/')
def index():
    ##### Cards Dashboard #####
    # === part 1: scope of available banks ===
    banks = fetch_all_banks()

    # === part 2: card ===
    card_banks = fetch_total_banks_and_cards()[0][0]
    card_cards = fetch_total_banks_and_cards()[0][1]

    # === part 2: bar ===
    top_k_banks = 5
    cards = fetch_cards_ranking(top_k_banks)

    fig1 = go.Figure()
    bank_names = [_[0] for _ in cards]
    card_counts = [_[1] for _ in cards]

    fig1.add_trace(go.Bar(x=bank_names, y=card_counts, name='S', 
                         marker=dict(color=card_counts, colorscale='dense'))) #Blues
    fig1.update_layout(autosize=True, title_x=0.5,
                      title_text=f'Quantity of top {top_k_banks} active cards in Taiwan',
                      xaxis_title='Banks', yaxis_title='Quantity',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    plot_1 = json.dumps(fig1, cls=py.utils.PlotlyJSONEncoder)

    # === part 3: bank name, card name, card_link and image ===
    release_intervals = 30
    latest = fetch_latest_cards(release_intervals)
    # first_date, bank_name, card_name, card_image, card_link
    if latest:
        plot_2 = latest
    else:
        plot_2 = release_intervals
    
    ##### Community Analysis #####
    # === part 1: wordclouds from ptt titles ===
    plot_3 = fetch_ptt_title_splitted()
    image_io = BytesIO()
    plot_3.save(image_io, 'PNG')
    image_url = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode()

    # === part 2: card scores from ptt articles ===
    scores = fetch_ptt_article_scores()
    sorted_scores = Counter(scores).most_common(7)

    fig4 = go.Figure()
    card_name4 = [_[0] for _ in sorted_scores]
    card_score4 = [_[1] for _ in sorted_scores]
    fig4.add_trace(go.Bar(x=card_score4, y=card_name4, orientation='h',
                         marker=dict(color=card_counts, colorscale='dense'))) #Blues
    fig4.update_layout(autosize=True, title_x=0.5,
                      title_text="What's the Most Highly-Regarded Credit Cards?",
                      xaxis_title='Scores of cards in PTT community', 
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    fig4.update_layout(xaxis={'categoryorder':'total descending'})
    plot_4 = json.dumps(fig4, cls=py.utils.PlotlyJSONEncoder)

    # === part 3: popular ptt articles ===
    articles = fetch_ptt_popular_articles()

    ##### Recent chats #####
    # === part 5: recent chats: create_dt, question, answer ===
    plot_5 = fetch_latest_chats()
        
    return render_template('index.html', banks=banks, card_banks=card_banks ,card_cards=card_cards, plot_1=plot_1, plot_2=plot_2, plot_4=plot_4, plot_3=image_url, articles=articles, plot_5=plot_5)


from server_producer.views import socketio_view
from server_producer.controllers import lang_controller