import sys
import json
import pytz
from datetime import datetime
from dotenv import load_dotenv
from wordcloud import WordCloud


load_dotenv()
sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_redis

TC_FONT_PATH = "server_producer/models/NotoSerifTC-Regular.otf"

# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')


def fetch_ptt_title_splitted():
    """
    retrieve the splitted ptt_titles from Redis
    """
    redis_conn = _get_redis()
    data = json.loads(redis_conn.get("ptt_title").decode("utf-8"))
    wc = WordCloud(
                font_path=TC_FONT_PATH,
                margin=2,
                background_color="rgba(255, 255, 255, 0)", mode="RGBA",
                max_font_size=100,
                width=700,
                height=550,
            ).generate(" ".join(data))
    return wc.to_image() 


def fetch_ptt_article_scores():
    """
    retrieve the scores of cards from Redis
    """
    redis_conn = _get_redis()
    data = json.loads(redis_conn.get("ptt_article").decode("utf-8"))
    return data


def fetch_ptt_popular_articles():
    """
    retrieve the popular articles of ptt from Redis
    """
    redis_conn = _get_redis()
    data = json.loads(redis_conn.get("ptt_popular_articles").decode("utf-8"))
    # filter for latest 5 articles with previous 100 words
    for i in data[:5]:
        i['article'] = i['article'][:100] + ' ...'
    return data[:5]


if __name__ == '__main__':
    print(fetch_ptt_popular_articles())
    