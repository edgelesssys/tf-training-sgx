# README

This repo contains multiple tests trying to figure out what goes wrong during the Gramine TF training workflow.

## Kubernetes

### AKS

Create a cluster with at least 2 nodes and SGX support:
```shell
CLUSTERNAME=sgx-cluster RESOURCEGROUP=myGroup NODES=2 \
    az aks create \
        --resource-group "$RESOURCEGROUP" \
        --name "$CLUSTERNAME" \
        --node-vm-size Standard_DC8s_v3 \
        --node-count "$NODES" \
        --network-plugin azure \
        --enable-addon confcom \
        --enable-sgxquotehelper \
        --network-plugin azure \
        --vm-set-type VirtualMachineScaleSets \
        --aks-custom-headers usegen2vm=true
```

### minikube

Start the cluster with enough resources:
```shell
minikube start --cpus=14 --memory=50GiB --mount --mount-string /var/run/aesmd/:/var/run/aesmd/
```

If links to the sgx devices don't exist in minikube, create the link manually:
```shell
minikube ssh
sudo mkdir /dev/sgx
sudo ln -s /dev/sgx_enclave /dev/sgx/enclave
sudo ln -s /dev/sgx_provision /dev/sgx/provision
```

Install SGX driver:
```
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.3.3/cert-manager.yaml
kubectl apply -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/sgx_plugin/overlays/epc-nfd/?ref=v0.23.0
```

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


## Results

### execve

Pods terminate successfully on both AKS and minikube

### gramine

Pods terminate successfully on both AKS and minikube

### marblerun

Pods terminate only on minikube. On AKS Pods sometimes get stuck in terminating indefinitely.
The log of a TF-training worker pod can be seen in `marblerun/terminate_deadlock.log`: multiple python threads keep running even though the Pod is supposed to terminate.

### marblerun-simulation

Same as [marblerun](#marblerun)
