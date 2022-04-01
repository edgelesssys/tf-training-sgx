# README

This setup runs a python script with MarbleRun in Gramine-SGX.
The Python program creates 128 threads, each of which does some simple math once a second, and then sleeps indefinitely.

## Training test

Start the training workflow:
```shell
kubectl create namespace threads
kubectl apply -f deployment.yaml
```

Watch the training:
```shell
kubectl logs -n threads threads -f
```

## Result on minikube

The pod can be terminated as expected.

## Result on AKS

The pod gets stuck in terminating indefinitely.

## Docker images

A key is needed to sign the Gramine enclaves.
Generate an RSA key using the following command:
```shell
openssl genrsa -out signing_key.pem 3072
```

Build the docker image using the following command:
```shell
DOCKER_BUILDKIT=1 docker build --secret id=signingkey,src=signing_key.pem -t localhost/threads.
```
