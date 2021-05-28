FROM abhioncbr/docker-superset:0.29.0rc5

HEALTHCHECK NONE

COPY ./src/ /home/superset/config/

COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
USER root
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
