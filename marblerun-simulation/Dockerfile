FROM alpine:latest AS premain
RUN wget -O /premain-libos -q  https://github.com/edgelesssys/marblerun/releases/download/v0.5.1/premain-libos && chmod +x /premain-libos

FROM tensorflow/tensorflow:2.7.0 AS release

RUN apt update && \
    apt install -y libssl-dev gnupg software-properties-common

RUN apt-key adv --fetch-keys https://packages.microsoft.com/keys/microsoft.asc && \
    apt-add-repository 'https://packages.microsoft.com/ubuntu/20.04/prod main' && \
    apt-key adv --fetch-keys https://packages.gramineproject.io/gramine.asc && \
    add-apt-repository 'deb [arch=amd64] https://packages.gramineproject.io/ 1.0 main' && \
    apt-key adv --fetch-keys https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key && \
    add-apt-repository 'https://download.01.org/intel-sgx/sgx_repo/ubuntu main'

RUN apt-get update && apt-get install -y \
    az-dcap-client \
    build-essential \
    libsgx-quote-ex-dev \
    libsgx-aesm-launch-plugin \
    libcurl4-openssl-dev \
    libprotobuf-c-dev \
    protobuf-c-compiler \
    python3-protobuf \
    python3-pip \
    gramine-dcap && \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir azure-storage-blob==2.1.0

WORKDIR /app
COPY ./* /app
ARG worker
COPY --from=premain /premain-libos /app
RUN --mount=type=secret,id=signingkey,dst=/app/signing_key.pem,required=true \
    make DEBUG=1 SGX=0 WORKER=${worker} && \
    mkdir tmp

ENTRYPOINT [ "gramine-direct", "python", "training.py" ]
