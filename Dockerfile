FROM python AS s2lc

# Install the required packages
RUN pip install --no-cache-dir redis flower flask flask-socketio

# PYTHONUNBUFFERED: Force stdin, stdout and stderr to be totally unbuffered. (equivalent to `python -u`)
# PYTHONHASHSEED: Enable hash randomization (equivalent to `python -R`)
# PYTHONDONTWRITEBYTECODE: Do not write byte files to disk, since we maintain it as readonly. (equivalent to `python -B`)
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1

# ENV FLOWER_DATA_DIR /data
# ENV PYTHONPATH ${FLOWER_DATA_DIR}
# WORKDIR $FLOWER_DATA_DIR
