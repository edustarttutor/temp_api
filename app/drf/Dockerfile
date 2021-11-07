FROM python:3.8.7-alpine3.12

RUN python -m pip install --upgrade pip
RUN apk add --virtual build-deps gcc python3-dev musl-dev\
     && apk add postgresql \
     && apk add postgresql-dev \
     && pip install psycopg2 \
     && apk add jpeg-dev zlib-dev libjpeg \
     && pip install Pillow \
     && apk del build-deps\
     && pip install gunicorn\
     && apk add nginx

RUN mkdir /app
RUN mkdir /app/drf
RUN mkdir /app/vue
RUN mkdir /run/nginx
WORKDIR /app/drf

COPY . .
COPY ./dist/default.conf /etc/nginx/conf.d/default.conf
RUN mv dist/frontpage /app/vue/
RUN mv dist/admin /app/vue/
RUN touch /run/nginx/nginx.pid

ENV PYTHONUNBUFFERED=1
ENV DRF_SECRET_KEY='boex@-*(!)vq8zm@3p5jj5z(eswbn#r_ja=x%2kdf*w=#8msgc'
ENV DRF_DEBUG=False
ENV DB_HOST='edustartdb.cdxs3bjiv0mp.us-east-2.rds.amazonaws.com'
ENV DB_NAME='d_edustart'
ENV DB_USER='donatus'
ENV DB_PASS='SEASONseason123456......'
ENV DB_PORT='5432'
ENV NODE_ENV='production'
ENV AWS_ACCESS_KEY_ID='AKIAXPXVH3AOYA6RLUVE'
ENV AWS_SECRET_ACCESS_KEY='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'


RUN pip install -r requirements.txt

EXPOSE 8084
EXPOSE 80

ENTRYPOINT [ "sh", "entry.sh" ]