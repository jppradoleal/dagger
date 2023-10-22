import pulumi
import pulumi_kubernetes as k8s


def create_provider(kubecfg, cluster):
    return k8s.Provider(
        "provider",
        kubeconfig=kubecfg,
        opts=pulumi.ResourceOptions(depends_on=[cluster]),
    )


def create_namespace(provider, name, labels):
    return k8s.core.v1.Namespace(
        name,
        metadata=k8s.meta.v1.ObjectMetaArgs(labels=labels, name="dagger-ns"),
        opts=pulumi.ResourceOptions(provider=provider, depends_on=[provider]),
    )


def install_postgres_chart(
    provider, name, namespace, replicas, password, database_name
):
    install_postgis_script = (
        "CREATE EXTENSION IF NOT EXISTS postgis; SELECT PostGIS_Version();"
    )

    return k8s.helm.v3.Release(
        name,
        chart="postgresql",
        version="12.12.5",
        namespace=namespace.metadata.name,
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://charts.bitnami.com/bitnami",
        ),
        skip_crds=True,
        values={
            "architecture": "replication",
            "readReplicas": {
                "replicaCount": replicas,
            },
            "auth": {
                "enablePostgresUser": True,
                "postgresPassword": password,
                "replicationPassword": password,
                "database": database_name,
            },
            "global": {"storageClass": "linode-block-storage"},
            "primary": {
                "initdb": {
                    "scripts": {"00_init_extensions.sql": install_postgis_script}
                }
            },
            "image": {"debug": True},
        },
        opts=pulumi.ResourceOptions(provider=provider, depends_on=[namespace]),
    )


dagger_labels = {"app": "dagger"}


def create_app_deployment(
    name,
    provider,
    namespace,
    database,
    database_user,
    database_password,
    database_name,
    labels,
    replicas,
    env="DEV",
):
    database_service_url = pulumi.Output.all(
        namespace.metadata.name, database.status.name
    ).apply(
        lambda args: f"{args[1]}-postgresql-primary.{args[0]}.svc.cluster.local:5432"
    )

    database_url = database_service_url.apply(
        lambda url: f"postgresql://{database_user}:{database_password}@{url}/{database_name}"
    )

    return k8s.apps.v1.Deployment(
        name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            namespace=namespace.metadata.name,
        ),
        spec=k8s.apps.v1.DeploymentSpecArgs(
            selector=k8s.meta.v1.LabelSelectorArgs(match_labels=labels),
            replicas=replicas,
            template=k8s.core.v1.PodTemplateSpecArgs(
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    labels=labels,
                    namespace=namespace.metadata.name,
                ),
                spec=k8s.core.v1.PodSpecArgs(
                    containers=[
                        k8s.core.v1.ContainerArgs(
                            name="dagger",
                            image="ghcr.io/jppradoleal/dagger:latest",
                            env=[
                                k8s.core.v1.EnvVarArgs(
                                    name="DATABASE_URL",
                                    value=database_url,
                                ),
                                k8s.core.v1.EnvVarArgs(
                                    name="PGPASSWORD", value=database_password
                                ),
                                k8s.core.v1.EnvVarArgs(
                                    name="PGUSER", value=database_user
                                ),
                                k8s.core.v1.EnvVarArgs(
                                    name="PGDATABASE", value=database_name
                                ),
                                k8s.core.v1.EnvVarArgs(name="ENV", value=env),
                            ],
                            ports=[
                                k8s.core.v1.ContainerPortArgs(container_port=8000),
                            ],
                        ),
                    ],
                ),
            ),
        ),
        opts=pulumi.ResourceOptions(
            provider=provider, depends_on=[namespace, database]
        ),
    )


def create_app_service(name, provider, namespace, app_deployment, labels):
    return k8s.core.v1.Service(
        name,
        spec=k8s.core.v1.ServiceSpecArgs(
            ports=[
                k8s.core.v1.ServicePortArgs(
                    port=8000,
                    target_port=8000,
                    protocol="TCP",
                ),
            ],
            selector={
                **labels,
            },
        ),
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=name,
            namespace=namespace.metadata.name,
        ),
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[
                app_deployment,
            ],
        ),
    )


def install_nginx_ingress(name, provider, namespace, depends_on):
    return k8s.helm.v3.Release(
        name,
        chart="ingress-nginx",
        namespace=namespace.metadata.name,
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
            depends_on=depends_on,
        ),
    )


def create_ingress(name, provider, namespace, host, target_service_name, depends_on):
    return k8s.networking.v1.Ingress(
        name,
        spec=k8s.networking.v1.IngressSpecArgs(
            rules=[
                k8s.networking.v1.IngressRuleArgs(
                    host=host,
                    http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                        paths=[
                            k8s.networking.v1.HTTPIngressPathArgs(
                                path="/",
                                path_type="Prefix",
                                backend=k8s.networking.v1.IngressBackendArgs(
                                    service=k8s.networking.v1.IngressServiceBackendArgs(
                                        name=target_service_name,
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
            name=name,
            namespace=namespace.metadata.name,
        ),
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=depends_on,
        ),
    )
