# README

This setup runs MarbleRun with TF-Training in SGX.

## Cluster setup

Install KubeFlow training operator:
```shell
kubectl apply -k "github.com/kubeflow/training-operator/manifests/overlays/standalone?ref=v1.3.0"
```

Create registry credential secret:
```shell
kubectl create secret generic regcred \
    --namespace=kubeflow \
    --from-file=.dockerconfigjson="$HOME/.docker/config.json" \
    --type=kubernetes.io/dockerconfigjson
```

### `minikube` setup

Start the cluster with enough resources and sgx devices:
```shell
minikube start --cpus=7 --memory=50GiB --mount --mount-string /dev/sgx/:/dev/sgx/
```

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

Pods sometimes don't terminate after training has finished.
Some python threads keep running in the enclave.

Resulting log file of a worker pod can be seen in `terminate_deadlock.log`

## Docker images

A key is needed to sign the Gramine enclaves.
Generate an RSA key using the following command:
```shell
openssl genrsa -out signing_key.pem 3072
```

Build the docker image using the following command:
```shell
DOCKER_BUILDKIT=1 docker build --build-arg worker=0 --secret id=signingkey,src=signing_key.pem -t localhost/tf-training:marblerun .
DOCKER_BUILDKIT=1 docker build --build-arg worker=1 --secret id=signingkey,src=signing_key.pem -t localhost/tf-training:marblerun-worker .
```

