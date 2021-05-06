# GKE Remove abandoned PV disks

This script aim is to find Google Compute disks with names matching the regex that were
part of GKE cluster (created with PVC/PV) and are abandoned, which means
there's no connection between disks and the cluster anymore, so they can be removed.

## How to run

```
python3 main.py <parameters>
```

where parameters are:

```
--kube-config
Kube config file location

--remove
Invokes gcloud delete commands based on findings

--dry-run
Prints the commands to be executed instead of executing them

--project-id
Google Cloud project ID where both GKE cluster and disks are.

--disk-regex
Regex to match disks' names against like "gke-my-cluster-.*pvc.*"

--kube-context
Kube context name to use against a cluster.

--zone
Zone the disk is created in if disks are zonal.

--replica-zones
as space separated string of zones the cluster is spread around like "europe-west1-b europe-west1-d" which assumes disks were also spread between these zones

--region
Regions the cluster and disks are created in like "europe-west1", required for --replica-zones
```

Example run:

```
python3 main.py --project-id random-project-id --disk-regex "gke-my-cluster.*pvc.*" --kube-context my-cluster --replica-zones="europe-west1-b europe-west1-d" --region europe-west1 --remove --dry-run

```
