ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:3.14
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

COPY run.sh /
COPY sdm630_emulator.py /sdm630_emulator.py
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]