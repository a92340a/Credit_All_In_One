import os
import sys
from dotenv import load_dotenv
from airflow.decorators import dag
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

sys.path.append('../Credit_All_In_One/')
from data_pipeline.etl_utils import get_chroma_content
from data_pipeline.fetch_credit_info import fetch_from_mongodb, insert_into_pgsql
from data_pipeline.split_ptt_words import split_ptt_title, score_ptt_article
from data_pipeline.retrieve_ptt_popular_articles import retrieve_popular_articles


load_dotenv()

default_args = {
    'owner': 'Finn',
    'start_date': datetime(2023, 10, 10, 0, 0),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=10)
}



@dag(tags=['daily_pgsql_and_redis_etl'], default_args=default_args, 
     dag_id="daily_pgsql_and_redis_etl",
     schedule_interval='@daily', catchup=True)
def dag_batch_bs():
    start_task = EmptyOperator(task_id="start_task")
    
    check_chroma_contents_at_the_start = PythonOperator(task_id="check_chroma_contents_at_the_start", 
                                      python_callable=get_chroma_content)
     
    update_credit_info_from_mongo = PythonOperator(task_id="update_credit_info_from_mongo", 
                                      python_callable=fetch_from_mongodb)

    update_credit_info_into_pgsql = PythonOperator(task_id="update_credit_info_into_pgsql", 
                                      python_callable=insert_into_pgsql)
    
    update_ptt_title_into_redis = PythonOperator(task_id="update_ptt_title_into_redis", 
                                      python_callable=split_ptt_title)
    
    update_ptt_articles_into_redis = PythonOperator(task_id="update_ptt_articles_into_redis", 
                                      python_callable=score_ptt_article)
    
    update_ptt_popular_articles_into_redis = PythonOperator(task_id="update_ptt_popular_articles_into_redis", 
                                      python_callable=retrieve_popular_articles)

    check_chroma_contents_at_the_end = PythonOperator(task_id="check_chroma_contents_at_the_end", 
                                      python_callable=get_chroma_content)
    
    end_task = EmptyOperator(task_id="end_task")
    
    start_task >> check_chroma_contents_at_the_start >> update_credit_info_from_mongo >> update_credit_info_into_pgsql
    update_credit_info_into_pgsql >> [update_ptt_title_into_redis, update_ptt_articles_into_redis, update_ptt_popular_articles_into_redis] >> check_chroma_contents_at_the_end
    check_chroma_contents_at_the_end >> end_task
    

dag_batch_bs()