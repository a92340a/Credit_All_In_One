import os
import json
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, request, render_template
from flask_socketio import SocketIO
from flask_sqlalchemy import Model, SQLAlchemy
from google.cloud.pubsublite.cloudpubsub import PublisherClient
from google.cloud.pubsublite.types import MessageMetadata

import plotly as py
import plotly.graph_objects as go

from server_producer.models.hot_cards_model import fetch_cards_ranking, fetch_total_cards, fetch_latest_cards
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
    # === part 1: card ===
    card_1 = fetch_total_cards()[0][0]
    # === part 1: bar ===
    top_k = 5
    cards = fetch_cards_ranking(top_k)

    fig = go.Figure()
    bank_names = [_[0] for _ in cards]
    card_counts = [_[1] for _ in cards]

    fig.add_trace(go.Bar(x=bank_names, y=card_counts, name='S', 
                         marker=dict(color=card_counts, colorscale='dense'))) #Blues
    fig.update_layout(autosize=True, title_x=0.5,
                      title_text=f'Quantity of top {top_k} active cards in Taiwan',
                      xaxis_title='Banks', yaxis_title='Quantity',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    plot_1 = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)

    # === part 2: bank name, card name, url and image ===
    latest = fetch_latest_cards()
    if latest:
        plot_2 = latest
    else:
        plot_2 = 'No new release in these 7 days!'
    
    # === part 5: recent chats: create_dt, question, answer ===
    plot_5 = fetch_latest_chats()
    
    # pie_color = go.Figure(go.Pie(labels=distinct_color_name, values=distinct_color_freq,
    #                              showlegend=True, marker=dict(colors=colors)))
    # pie_color.update_layout(title_text='Product sold percentage in different colors',
    #                         xaxis_title='', yaxis_title='Quantity')
    # plot_2 = json.dumps(pie_color, cls=py.utils.PlotlyJSONEncoder)
    
    return render_template('index.html', card_1=card_1, plot_1=plot_1, plot_2=plot_2, plot_5=plot_5)


from server_producer.views import socketio_view
from server_producer.controllers import lang_controller