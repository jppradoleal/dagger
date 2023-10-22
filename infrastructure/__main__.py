"""An AWS Python Pulumi program"""

import base64

import pulumi
from kube_specs import (
    create_app_deployment,
    create_app_service,
    create_ingress,
    create_namespace,
    create_provider,
    install_nginx_ingress,
    install_postgres_chart,
)
from linode_specs import create_cluster

dagger_cluster = create_cluster()


pulumi.export("lke-kubeconfig", dagger_cluster.kubeconfig)
pulumi.export("lke-api-endpoint", dagger_cluster.api_endpoints)

kubecfg = dagger_cluster.kubeconfig.apply(lambda v: base64.b64decode(v).decode("utf-8"))

provider = create_provider(kubecfg=kubecfg, cluster=dagger_cluster)

app_labels = {"app": "mongo"}

dagger_ns = create_namespace(provider=provider, name="dagger-ns", labels=app_labels)

database_password = "secret-root-password"

postgresdb = install_postgres_chart(
    provider=provider,
    name="postgres",
    namespace=dagger_ns,
    replicas=3,
    password=database_password,
    database_name="dagger",
)

dagger_dp = create_app_deployment(
    "dagger-deployment",
    provider=provider,
    namespace=dagger_ns,
    database=postgresdb,
    database_password=database_password,
    labels=app_labels,
    replicas=3,
)

dagger_svc = create_app_service(
    "dagger-svc",
    provider=provider,
    namespace=dagger_ns,
    app_deployment=dagger_dp,
    labels=app_labels,
)

nginx_ingress = install_nginx_ingress(
    "nginx-ingress", provider=provider, namespace=dagger_ns, depends_on=[dagger_dp]
)

dagger_ingress = create_ingress(
    "dagger-ingress",
    provider=provider,
    namespace=dagger_ns,
    # Preciso encontrar uma forma de acessar o NodeBalancer criado pelo Linode
    # para poder pegar o host automaticamente. Ou talvez forçar meu domínio.
    host="143-42-178-51.ip.linodeusercontent.com",
    target_service_name="dagger-svc",
    depends_on=[nginx_ingress],
)
