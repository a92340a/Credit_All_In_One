import os
import sys
from dotenv import load_dotenv
from airflow.decorators import dag
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

sys.path.append('../Credit_All_In_One/')
import crawler 
from crawler.utils import list_target_url, get_chroma_schema, crawl_banks
from crawler.crawl_batch_bs2 import crawling_dbs, crawling_yuanta, crawling_fareast, crawling_changhua,\
    crawling_kaohsiung, crawling_kgi, crawling_taichung, crawling_shanghai, crawling_sunny, crawling_rakuten


load_dotenv()

default_args = {
    'owner': 'Finn',
    'start_date': datetime(2023, 9, 25, 23, 0),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=10)
}


BANK = [    
    {'function':crawling_dbs, 'url':['https://www.dbs.com.tw/personal-zh/cards/dbs-credit-cards/default.page']},
    {'function':crawling_yuanta, 'url':['https://www.yuantabank.com.tw/bank/creditCard/creditCard/list.do']},
    {'function':crawling_fareast, 'url':['https://www.feib.com.tw/introduce/cardInfo?type=1',
                    'https://www.feib.com.tw/introduce/cardInfo?type=2']},
    {'function':crawling_changhua, 'url':['https://www.bankchb.com/frontend/mashup.jsp?funcId=f0f6e5d215']},
    {'function':crawling_kaohsiung, 'url':['https://www.bok.com.tw/credit-card']},
    {'function':crawling_kgi, 'url':['https://www.kgibank.com.tw/zh-tw/personal/credit-card/list']},
    {'function':crawling_taichung, 'url':['https://www.tcbbank.com.tw/CreditCard/J_02.html']},
    {'function':crawling_shanghai, 'url':['https://www.scsb.com.tw/content/card/card03.html']},
    {'function':crawling_sunny, 'url':['https://www.sunnybank.com.tw/net/Page/Smenu/125']},
    {'function':crawling_rakuten, 'url':['https://www.card.rakuten.com.tw/corp/product/']},
]


@dag(tags=['crawler-official-websites-on-small-banks'], default_args=default_args, 
     dag_id="crawler-official-websites-on-small-banks",
     schedule_interval='@daily', catchup=False)
def dag_batch_bs2():
    start_task = EmptyOperator(task_id="start_task")
    
    list_url = PythonOperator(task_id="list_all_url", 
                                      python_callable=list_target_url,
                                      op_args=[BANK])
     
    check_chroma_schema_at_the_start = PythonOperator(task_id="check_chroma_schema_at_the_start", 
                                      python_callable=get_chroma_schema)

    crawl_main_banks = PythonOperator(task_id="crawl_main_banks_by_beautifulsoups", 
                                      python_callable=crawl_banks)
    
    check_chroma_schema_at_the_end = PythonOperator(task_id="check_chroma_schema_at_the_end", 
                                      python_callable=get_chroma_schema)
    
    end_task = EmptyOperator(task_id="end_task")
    
    start_task >> list_url >> check_chroma_schema_at_the_start >> crawl_main_banks 
    crawl_main_banks >> check_chroma_schema_at_the_end >> end_task

dag_batch_bs2()