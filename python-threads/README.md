# README

This setup runs a python script with MarbleRun in Gramine-SGX.
The Python program creates 128 threads, each of which does some simple math once a second, and then sleeps indefinitely.

## Install MarbleRun

You can deploy MarbleRun on Kubernetes using the CLI:
```shell
marblerun install
marblerun check
kubectl -n marblerun port-forward svc/coordinator-client-api 4433:4433 --address localhost >/dev/null &
```

If you wish to run MarbleRun standalone, outside of Kubernetes, you can use our docker image:
```shell
docker run -it --rm \
   --network host \
   --device /dev/sgx_enclave \
   --device /dev/sgx_provision \
   -v /dev/sgx:/dev/sgx \
   ghcr.io/edgelesssys/coordinator
```

After the MarbleRun Coordinator has started, you will need to set the manifest.
```shell
marblerun manifest set manifest.json localhost:4433
```

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
