# README

This setup runs TF-Training with Gramine in SGX. The Python program is called from a Go application using `execve` to simulate a heavily simplified behavior of MarbleRun's premain.

## Training test

Start the training workflow:
```shell
kubectl apply -f deployment.yaml
```

Watch the training:
```shell
kubectl logs -n kubeflow d-paddles-training-chief-0 -f
kubectl logs -n kubeflow d-paddles-training-worker-0 -f
kubectl logs -n kubeflow d-paddles-training-ps-0 -f
```

## Result on AKS

Pods terminate successfully after training has finished.

## Docker images

A key is needed to sign the Gramine enclaves.
Generate an RSA key using the following command:
```shell
openssl genrsa -3 -out signing_key.pem 3072
```

Build the docker image using the following command:
```shell
go build -o caller ./caller.go
DOCKER_BUILDKIT=1 docker build --build-arg worker=0 --secret id=signingkey,src=signing_key.pem -t localhost/tf-training:execve.
DOCKER_BUILDKIT=1 docker build --build-arg worker=1 --secret id=signingkey,src=signing_key.pem -t localhost/tf-training:execve-worker .
```

