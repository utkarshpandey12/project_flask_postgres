FROM python:3.10-slim-bullseye

# Install Nginx, uWSGI, Supervisor
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential nginx supervisor \
    && pip install --no-cache-dir uwsgi \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove build-essential \
    && find /usr/local -depth \
    \( \
        \( -type d -a -name test -o -name tests \) \
        -o \
        \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    \) -exec rm -rf '{}' + \
    && rm /etc/nginx/nginx.conf \
    && rm /etc/nginx/sites-enabled/default \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

# Copy Nginx, uWSGI and Supervisor configuration files
COPY docker/nginx.conf /etc/nginx/
COPY docker/uwsgi.ini /etc/uwsgi/
COPY docker/supervisord.conf /etc/supervisor/conf.d/

# Copy stop-supervisor.sh to kill Supervisor and sub-tasks on app failure
COPY docker/stop-supervisor.sh /etc/supervisor/stop-supervisor.sh
RUN chmod +x /etc/supervisor/stop-supervisor.sh

# Install app requirements
COPY requirements.txt /tmp/requirements.txt
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove build-essential \
    && rm /tmp/requirements.txt

# Copy application
COPY . /var/www/app

EXPOSE 80

ENTRYPOINT ["/usr/bin/supervisord"]
CMD ["-c", "/etc/supervisor/conf.d/supervisord.conf"]
