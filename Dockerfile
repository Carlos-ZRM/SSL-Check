FROM python:alpine3.7
RUN  apk add --no-cache build-base openssl-dev libffi-dev curl tzdata
WORKDIR /app
COPY app/ /app
VOLUME ["/app/csv"]
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "/bin/sh","entrypoint.sh" ]