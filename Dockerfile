FROM debian

RUN apt-get update && apt-get install -y \
    maven \
    python-pip \
    libev-dev \
    python-dev \
    && rm -rf /var/lib/apt/lists/*


COPY setup.py /tmp/wsgi_benchmark/setup.py
RUN cd /tmp/wsgi_benchmark \
    && pip download . \
    && pip install --upgrade *.tar.gz *.whl \
    && rm -rf /tmp/wsgi_benchmark


COPY gatling /wsgi_benchmark/gatling
RUN cd /wsgi_benchmark/gatling \
    && mvn -Dgatling.skip=true test-compile integration-test


COPY . /wsgi_benchmark
RUN cd /wsgi_benchmark && pip install .


WORKDIR /wsgi_benchmark
