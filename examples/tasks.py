import os
import time
import logging
import celery.signals
from datetime import datetime
import json
import subprocess

from celery import Celery
from celery import current_task

# celery
logging.getLogger('celery').setLevel(logging.ERROR)
app = Celery("tasks",
             broker=os.environ.get('CELERY_BROKER_URL'),
             backend=os.environ.get('CELERY_RESULT_BACKEND'),
             )
app.conf.accept_content = ['pickle', 'json', 'msgpack', 'yaml']
app.conf.worker_send_task_events = True

class JsonFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.extra_fields = kwargs.pop('extra_fields', [])
        super().__init__(*args, **kwargs)

    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        for field in self.extra_fields:
            if hasattr(record, field):
                log_record[field] = getattr(record, field)
        return json.dumps(log_record, ensure_ascii=False)

# カスタムロガー
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(JsonFormatter(extra_fields=['task_id']))
logger.addHandler(console_handler)

# celery既存のロガーセットアップを無視する
@celery.signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    pass

# 投入テスト
# python -m "from tasks import longjob; longjob.delay()"
# ジョブを変更したら、ワーカープロセスを再起動する必要がある
@app.task(bind=True)
def longjob(self):
    task_id = self.request.id  # task_idにアクセス

    process = subprocess.Popen(
        "top",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # 出力をバイナリではなく文字列で読み取る
        shell=True, # ターミナルに入力するコマンド文字列がそのまま入る
    )
    for line in process.stdout:
        logger.info(line.strip(), extra={'task_id': task_id})
    for line in process.stderr:
        logger.info(line.strip(), extra={'task_id': task_id})

    process.wait()
