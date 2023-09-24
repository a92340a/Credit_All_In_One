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
from crawler.crawl_batch_bs import crawling_taishin, crawling_cathay, crawling_hsbc, \
    crawling_fubon, crawling_sinopac, crawling_huanan, crawling_first, crawling_land, crawling_chartered


load_dotenv()

default_args = {
    'owner': 'Finn',
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=10)
}


BANK = [
    {'function':crawling_taishin, 'url':['https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html?type=type2',
                'https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html?type=type3',
                'https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html?type=type4']},
    {'function':crawling_cathay, 'url':['https://www.cathaybk.com.tw/cathaybk/personal/product/credit-card/cards/']},
    {'function':crawling_hsbc, 'url':['https://www.hsbc.com.tw/credit-cards/']},
    {'function':crawling_fubon, 'url':['https://www.fubon.com/banking/personal/credit_card/all_card/all_card.htm']},
    {'function':crawling_sinopac, 'url':['https://bank.sinopac.com/sinopacBT/personal/credit-card/introduction/list.html']},
    {'function':crawling_huanan, 'url':['https://card.hncb.com.tw/wps/portal/card/area1/cardall/']},
    {'function':crawling_first, 'url':['https://card.firstbank.com.tw/sites/card/touch/1565690685468']},
    {'function':crawling_land, 'url':['https://www.landbank.com.tw/Category/Items/%E9%8A%80%E8%A1%8C%E5%8D%A1_',
                'https://www.landbank.com.tw/Category/Items/%E8%AA%8D%E5%90%8C%E5%8D%A1%E3%80%81%E8%81%AF%E5%90%8D%E5%8D%A1%E2%80%94JCB%E7%B3%BB%E5%88%97']},
    {'function':crawling_chartered, 'url':['https://www.sc.com/tw/credit-cards/']},    
]


@dag(tags=['crawler-official-websites-on-main-banks'], default_args=default_args, 
     dag_id="crawler-official-websites-on-main-banks",
     schedule_interval='@daily', catchup=False)
def dag_batch_bs():
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

dag_batch_bs()