import sys
from airflow.decorators import dag
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

sys.path.append('../Credit_All_In_One/')
from data_pipeline.etl_utils import get_chroma_content
from data_pipeline.credit_docs_transformation import docs_comparing_and_embedding


default_args = {
    'owner': 'Finn',
    'start_date': datetime(2023, 10, 10, 0, 0),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=10)
}



@dag(tags=['daily_chroma_embedding_etl'], default_args=default_args, 
     dag_id="daily_chroma_embedding_etl",
     schedule_interval='@daily', catchup=True)
def dag_batch_bs():
    start_task = EmptyOperator(task_id="start_task")
    
    check_chroma_contents_at_the_start = PythonOperator(task_id="check_chroma_contents_at_the_start", 
                                      python_callable=get_chroma_content)
     
    docs_embedding = PythonOperator(task_id="docs_embedding", 
                                      python_callable=docs_comparing_and_embedding)
    
    check_chroma_contens_at_the_end = PythonOperator(task_id="check_chroma_contents_at_the_end", 
                                      python_callable=get_chroma_content)
    
    end_task = EmptyOperator(task_id="end_task")
    
    start_task >> check_chroma_contents_at_the_start >> docs_embedding >> check_chroma_contens_at_the_end >> end_task 
    

dag_batch_bs()