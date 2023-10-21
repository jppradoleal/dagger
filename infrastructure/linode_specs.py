import pulumi_linode as linode


def create_cluster(worker_count=3, worker_type="g6-standard-1"):
    return linode.LkeCluster(
        "dagger-cluster",
        k8s_version="1.26",
        label="dagger-cluster",
        pools=[linode.LkeClusterPoolArgs(count=worker_count, type=worker_type)],
        region="us-east",
        tags=["dev"],
    )
