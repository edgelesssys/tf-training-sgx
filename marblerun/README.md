# README

This setup runs MarbleRun with TF-Training in SGX.

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
openssl genrsa -3 -out signing_key.pem 3072
```

Build the docker image using the following command:
```shell
DOCKER_BUILDKIT=1 docker build --build-arg worker=0 --secret id=signingkey,src=signing_key.pem -t localhost/tf-training:marblerun .
DOCKER_BUILDKIT=1 docker build --build-arg worker=1 --secret id=signingkey,src=signing_key.pem -t localhost/tf-training:marblerun-worker .
```

