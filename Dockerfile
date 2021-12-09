FROM python

COPY setup.py /icij/
COPY src /icij/src
WORKDIR /icij
RUN apt update && apt upgrade -y
RUN apt install postgresql-client -y
RUN pip3 install -q -e /icij

ENV FTM_STORE_URI=postgresql://datastore:datastore@datastore/datastore
