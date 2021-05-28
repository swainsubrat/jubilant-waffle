FROM 611951854009.dkr.ecr.us-east-1.amazonaws.com/nexa_base:1.3.1
ARG NEXA_PYTHON_VERSION
USER root
HEALTHCHECK NONE

# since we are loading dataframe pickles, we need pandas
# RUN  conda uninstall pandas -y \
RUN /opt/conda/bin/conda install --yes \
    jinja2==2.11.2 \
    ldap3==2.8.1 \
    Flask==1.1.2 \
    gunicorn==20.0.4 \
    gevent==1.4.0  \
    greenlet==0.4.16 \
    && pip install   --no-cache-dir   --trusted-host pypi.python.org \
    mysql-connector-python==8.0.19 \
    bleach==3.3.0 \
    flask_jwt_extended==3.25.0 \
    avinit==1.2.2 \
    itsdangerous==1.1.0 \
    # python-dateutil==2.8.1 \ to be installed after pandas is removed
    # pytz==2020.1 \
    && pip install   --no-cache-dir   --trusted-host pypi.python.org \
    msal==1.10.0 \
    Flask-Session==0.3.2 \
    && pip uninstall bson -y \
    && /opt/conda/bin/conda clean -afy \
    && find /opt/conda/ -follow -type f -name '*.a' -delete \
    && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete \
    # for resolving anchore no private key policy
    && rm /opt/conda/lib/python3.7/site-packages/gevent/tests/*.pem \
    && rm /opt/conda/lib/python3.7/site-packages/gevent/tests/*.key

RUN pip install https://jithu-dto.s3.ap-south-1.amazonaws.com/nexa/NEXA-$NEXA_PYTHON_VERSION-py3-none-any.whl

COPY ./src/  /src
RUN chown -R dto_user:dto_users /src/ && \
    mkdir -p /src/logs/ && \
    mkdir -p /src/temp/ && \
    chown -R dto_user:dto_users /src/logs/ && \
    chown -R dto_user:dto_users /src/temp/

USER dto_user
WORKDIR /src

CMD  ["tini", "--", "wait-for-it", \
    "--service", "pgbouncer:6432",\
    "--service", "rabbitmq:5672",\
    "--service", "redis:6379",\
    "--timeout", "60", \
    "--", "gunicorn", "--workers=1", "--threads=4", "--log-level=warning", "--worker-class=gevent", "--timeout=600","--bind=0.0.0.0:5000", "app:app"]
