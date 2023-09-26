from datetime import datetime, timedelta, timezone
from airflow.decorators import dag
from airflow.utils.db import provide_session
from airflow.models import XCom
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator


default_args = {
    'owner': 'Finn',
    'start_date': datetime(2023, 9, 25, 21, 0),
    'email_on_failure': False,
    'email_on_retry': False,
}


@provide_session
def cleanup_xcom(session=None, **context):
    ts_limit = datetime.now(timezone.utc) - timedelta(days=2)
    session.query(XCom).filter(XCom.execution_date < ts_limit).delete(synchronize_session=False)
    session.commit()


@dag(tags=['crawler_cleanup_xcom'], default_args=default_args, 
     dag_id='crawler_cleanup_xcom',
     schedule_interval='@daily', catchup=False)
def clean():
    start_task = EmptyOperator(task_id="start_task")

    clean_xcom = PythonOperator(
        task_id="clean_xcom",
        python_callable = cleanup_xcom,
    )

    end_task = EmptyOperator(task_id="end_task")
    
    start_task >> clean_xcom >> end_task

clean()