"""An AWS Python Pulumi program"""

import pulumi
import pulumi_kubernetes as k8s
import pulumi_linode as linode

cluster = linode.LkeCluster(
    "dagger-cluster",
    k8s_version="1.21",
    label="dagger-cluster",
    pools=[linode.LkeClusterPoolArgs(count=3, type="g6-standard-1")],
    region="us-east",
    tags=["dev"],
)

pulumi.export("lke-kubeconfig", cluster.kubeconfig)
pulumi.export("lke-api-endpoint", cluster.api_endpoints)

provider = k8s.Provider("provider", kubeconfig=cluster.kubeconfig)

app_labels = {"app": "mongo"}

dagger_ns = k8s.core.v1.Namespace(
    "dagger-ns",
    metadata=k8s.meta.v1.ObjectMetaArgs(labels=app_labels, name="dagger-ns"),
    opts=pulumi.ResourceOptions(provider=provider),
)

database_password = "secret-root-password"

postgresdb = k8s.helm.v3.Release(
    "postgres",
    chart="postgresql",
    namespace=dagger_ns.metadata.name,
    repository_opts=k8s.helm.v3.RepositoryOptsArgs(
        repo="https://charts.bitnami.com/bitnami",
    ),
    skip_crds=True,
    values={
        "architecture": "replication",
        "readReplicas": {
            "replicaCount": 3,
        },
        "auth": {
            "postgresPassword": database_password,
            "replicationPassword": database_password,
            "enablePostgresUser": True,
        },
    },
    opts=pulumi.ResourceOptions(provider=provider, depends_on=[dagger_ns]),
)

dagger_labels = {"app": "dagger"}

dagger_dp = k8s.apps.v1.Deployment(
    "dagger-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        namespace=dagger_ns.metadata.name,
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=dagger_labels),
        replicas=3,
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels=dagger_labels,
                namespace=dagger_ns.metadata.name,
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name="dagger",
                        image="ghcr.io/jppradoleal/dagger:latest",
                        env=[
                            k8s.core.v1.EnvVarArgs(
                                name="DATABASE_URL",
                                value="postgresql://postgres:{database_password}@postgresql-primary/dagger",
                            ),
                            k8s.core.v1.EnvVarArgs(name="ENV", value="dev"),
                        ],
                        ports=[
                            k8s.core.v1.ContainerPortArgs(container_port=8000),
                        ],
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=provider, depends_on=[dagger_ns, postgresdb]),
)

dagger_svc = k8s.core.v1.Service(
    "dagger-svc",
    spec=k8s.core.v1.ServiceSpecArgs(
        ports=[
            k8s.core.v1.ServicePortArgs(
                port=8000,
                target_port=8000,
                protocol="TCP",
            ),
        ],
        selector={
            **dagger_labels,
        },
    ),
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="dagger-service",
        namespace=dagger_ns.metadata.name,
    ),
    opts=pulumi.ResourceOptions(
        provider=provider,
        depends_on=[
            dagger_dp,
        ],
    ),
)

nginx_ingress = k8s.helm.v3.Release(
    "nginx-ingress",
    chart="ingress-nginx",
    namespace=dagger_ns.metadata.name,
    repository_opts=k8s.helm.v3.RepositoryOptsArgs(
        repo="https://kubernetes.github.io/ingress-nginx",
    ),
    values={
        "controller": {
            "publishService": {
                "enabled": True,
            },
        }
    },
    opts=pulumi.ResourceOptions(
        provider=provider,
        depends_on=[
            dagger_dp,
        ],
    ),
)

dagger_ingress = k8s.networking.v1.Ingress(
    "dagger-ingress",
    spec=k8s.networking.v1.IngressSpecArgs(
        rules=[
            k8s.networking.v1.IngressRuleArgs(
                host="dagger.local",
                http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        k8s.networking.v1.HTTPIngressPathArgs(
                            path="/",
                            path_type="Exact",
                            backend=k8s.networking.v1.IngressBackendArgs(
                                service=k8s.networking.v1.IngressServiceBackendArgs(
                                    name="dagger-service",
                                    port=k8s.networking.v1.ServiceBackendPortArgs(
                                        number=8000,
                                    ),
                                ),
                            ),
                        ),
                    ],
                ),
            ),
        ],
    ),
    metadata=k8s.meta.v1.ObjectMetaArgs(
        annotations={
            "kubernetes.io/ingress.class": "nginx",
        },
        name="dagger",
        namespace=dagger_ns.metadata.name,
    ),
    opts=pulumi.ResourceOptions(
        provider=provider,
        depends_on=[
            nginx_ingress,
        ],
    ),
)
