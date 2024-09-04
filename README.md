立ち上げる。
```
docker compose up -d
```

ジョブを投入する。
```
docker compose exec worker /bin/sh -c 'python -c "from tasks import longjob; longjob.delay()"'
```
