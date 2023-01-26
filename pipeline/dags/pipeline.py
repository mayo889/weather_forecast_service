from datetime import datetime, timedelta
from os import path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

from operators.everyday_parser import last_day_parser
from operators.content import (transform_preds,
                               graph_predictions, graph_metrics)
from operators.predict import predict_and_save
from operators.train_and_finetune import train_and_save
from operators.db_tools import make_data_backup
from operators.paths import MODEL_PATH, MODEL_FILENAME


def file_exists(model_path):
    return path.isfile(model_path) 


with DAG(
    "dmls",
    default_args={
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 3,
        "retry_delay": timedelta(minutes=30),
    },
    description="Project",
    schedule_interval="0 8 * * *",
    start_date=datetime(2023, 1, 11),
    catchup=False,
    tags=["project"],
    is_paused_upon_creation=False
) as dag:

    start = EmptyOperator(
        task_id='start'
    )

    ########## PARSER ##########
    parser_op = PythonOperator(
        task_id='parser',
        python_callable=last_day_parser
    )

    ########## MODEL ##########
    def model_branch_function(): 
        if file_exists(path.join(MODEL_PATH, MODEL_FILENAME)):
            return "fine_tune_and_save"
        else:
            return "train_and_save"
    
    model_branch = BranchPythonOperator(
        task_id='model_branch',
        python_callable=model_branch_function,
    )
    fine_tune_op = PythonOperator(
        task_id='fine_tune_and_save',
        python_callable=lambda: train_and_save(finetune=True)
    )
    train_op = PythonOperator(
        task_id='train_and_save',
        python_callable=lambda: train_and_save()
    )
    model_end_branch = EmptyOperator(
        task_id='model_end_branch',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )
    make_predictions_op = PythonOperator(
        task_id='predict_and_save',
        python_callable=predict_and_save
    )

    ########## CONTENT ##########
    transform_preds_op = PythonOperator(
        task_id='transform_preds',
        python_callable=transform_preds
    )
    graph_preds_op = PythonOperator(
        task_id="graph_predictions",
        python_callable=graph_predictions
    )
    graph_metrics_op = PythonOperator(
        task_id="graph_metrics",
        python_callable=graph_metrics
    )

    ########## BACKUP ##########
    backup_op = PythonOperator(
        task_id='data_backup',
        python_callable=make_data_backup
    )

    end = EmptyOperator(
        task_id='end'
    )

    start >> parser_op >> model_branch
    model_branch >> [fine_tune_op, train_op] >> model_end_branch
    model_end_branch >> make_predictions_op
    make_predictions_op >> [transform_preds_op, graph_preds_op, graph_metrics_op] >> backup_op
    backup_op >> end
