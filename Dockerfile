FROM python:alpine3.7

ARG TZ='America/Sao_Paulo'
ENV DEFAULT_TZ ${TZ}

WORKDIR /app

COPY ./python/ /app

RUN pip3 install -r requirements.txt
RUN apk upgrade --update \
  && apk add -U tzdata \
  && cp /usr/share/zoneinfo/${DEFAULT_TZ} /etc/localtime \
  && apk del tzdata \
  && rm -rf \
  /var/cache/apk/*

CMD [ "python3", "app.py" ]