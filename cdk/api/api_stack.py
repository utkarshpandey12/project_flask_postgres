import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from .config import CONFIG


class ApiStage(cdk.Stage):
    def __init__(
        self,
        scope,
        id,
        *,
        env=None,
        outdir=None,
        api_name: str = None,
        env_name: str = None,
    ):
        super().__init__(scope, id, env=env, outdir=outdir)
        self.api_name = api_name
        self.api_name_capitalized = api_name.capitalize()
        ApiStack(
            self,
            f"{self.api_name_capitalized}ApiStack",
            api_name=api_name,
            env_name=env_name,
        )


class ApiStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api_name: str = None,
        env_name: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.api_name = api_name
        self.api_name_capitalized = api_name.capitalize()
        app_vpc = self.lookup_app_vpc()
        ecr_repo = self.lookup_ecr_repo()
        cluster = self.lookup_ecs_cluster(app_vpc=app_vpc)
        alb_security_group = self.lookup_alb_security_group()
        alb_listener = self.lookup_alb_listener(security_group=alb_security_group)
        aws_log_driver = self.create_aws_log_driver()
        task_definition = self.create_fargate_task_definition(
            env_name=env_name, ecr_repo=ecr_repo, log_driver=aws_log_driver
        )
        service = self.create_fargate_service(
            env_name=env_name,
            cluster=cluster,
            task_definition=task_definition,
        )
        self.create_target_group(
            env_name=env_name,
            app_vpc=app_vpc,
            alb_listener=alb_listener,
            service=service,
        )

    def lookup_app_vpc(self):
        vpc_id = ssm.StringParameter.value_from_lookup(self, "app-vpc-id")
        vpc = ec2.Vpc.from_lookup(self, "AppVpc", vpc_id=vpc_id)
        return vpc

    def lookup_ecr_repo(self):
        ecr_repo_arn = ssm.StringParameter.value_for_string_parameter(
            self, f"{self.api_name}-api-ecr-repo-arn"
        )
        ecr_repo_name = ssm.StringParameter.value_for_string_parameter(
            self, f"{self.api_name}-api-ecr-repo-name"
        )
        ecr_repo = ecr.Repository.from_repository_attributes(
            self,
            f"{self.api_name_capitalized}ApiEcrRepo",
            repository_arn=ecr_repo_arn,
            repository_name=ecr_repo_name,
        )
        return ecr_repo

    def lookup_ecs_cluster(self, app_vpc: ec2.IVpc = None) -> ecs.ICluster:
        cluster_name = ssm.StringParameter.value_for_string_parameter(
            self, "app-ecs-cluster-name"
        )
        cluster = ecs.Cluster.from_cluster_attributes(
            self,
            "AppEcsCluster",
            cluster_name=cluster_name,
            vpc=app_vpc,
            security_groups=[],
        )
        return cluster

    def lookup_alb_security_group(self) -> ec2.ISecurityGroup:
        security_group_id = ssm.StringParameter.value_from_lookup(
            self, "app-load-balancer-security-group-id"
        )
        security_group = ec2.SecurityGroup.from_lookup_by_id(
            self,
            "AppLoadBalancerSecurityGroup",
            security_group_id,
        )
        return security_group

    def lookup_alb_listener(self, security_group: ec2.ISecurityGroup = None):
        listener_arn = ssm.StringParameter.value_for_string_parameter(
            self, "app-load-balancer-https-listener-arn"
        )
        listener = elbv2.ApplicationListener.from_application_listener_attributes(
            self,
            "AppLoadBalancerHttpsListener",
            listener_arn=listener_arn,
            security_group=security_group,
        )
        return listener

    def create_aws_log_driver(self) -> ecs.AwsLogDriver:
        aws_log_driver = ecs.AwsLogDriver(
            stream_prefix=f"{self.api_name}-api", mode=ecs.AwsLogDriverMode.NON_BLOCKING
        )
        return aws_log_driver

    def create_fargate_task_definition(
        self,
        env_name: str = None,
        ecr_repo: ecr.IRepository = None,
        log_driver: ecs.LogDriver = None,
    ) -> ecs.FargateTaskDefinition:
        config = CONFIG[env_name]
        ecs_config = config["ecs"]
        db_secret_name = ssm.StringParameter.value_for_string_parameter(
            self, "app-db-secret-name"
        )
        db_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "AppDbSecret", db_secret_name
        )
        db_secret_env_var = ecs.Secret.from_secrets_manager(db_secret)

        redis_primary_address = ssm.StringParameter.value_for_string_parameter(
            self, "app-elasticache-replication-group-primary-address"
        )
        redis_primary_port = ssm.StringParameter.value_for_string_parameter(
            self, "app-elasticache-replication-group-primary-port"
        )
        s3_bucket_name_private = ssm.StringParameter.value_for_string_parameter(
            self,
            "app-s3-private-bucket-name",
        )
        s3_bucket_name_public = ssm.StringParameter.value_for_string_parameter(
            self,
            "app-s3-public-bucket-name",
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            f"{self.api_name_capitalized}ApiTaskDefinition",
            memory_limit_mib=ecs_config["memory_limit_mib"],
            cpu=ecs_config["cpu"],
        )
        task_definition.task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                ],
                resources=[
                    f"arn:aws:s3:::{s3_bucket_name_private}/*",
                    f"arn:aws:s3:::{s3_bucket_name_public}/*",
                ],
            )
        )
        task_definition.task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:ListBucket",
                ],
                resources=[
                    f"arn:aws:s3:::{s3_bucket_name_private}",
                    f"arn:aws:s3:::{s3_bucket_name_public}",
                ],
            )
        )
        container = task_definition.add_container(
            f"{self.api_name_capitalized}ApiContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr_repo, tag="latest"
            ),
            logging=log_driver,
            secrets={
                "DB_SECRET": db_secret_env_var,
            },
            environment={
                "DEBUG": str(config["debug"]),
                "ENABLE_CORS": str(config["enable_cors"]),
                "URL_PREFIX": f"/api/{self.api_name}",
                "REDIS_JOBS_HOST": redis_primary_address,
                "REDIS_JOBS_PORT": redis_primary_port,
                "REDIS_JOBS_DB": "0",
                "S3_BUCKET_NAME_PRIVATE": s3_bucket_name_private,
                "S3_BUCKET_NAME_PUBLIC": s3_bucket_name_public,
            },
        )
        container.add_port_mappings(ecs.PortMapping(container_port=80))
        return task_definition

    def create_fargate_service(
        self,
        env_name: str = None,
        cluster: ecs.ICluster = None,
        task_definition: ecs.FargateTaskDefinition = None,
    ):
        config = CONFIG[env_name]["ecs"]
        service = ecs.FargateService(
            self,
            f"{self.api_name_capitalized}ApiService",
            task_definition=task_definition,
            assign_public_ip=False,
            cluster=cluster,
            desired_count=config["desired_count"],
        )
        ssm.StringParameter(
            self,
            f"{self.api_name_capitalized}ApiServiceName",
            parameter_name=f"{self.api_name}-api-service-name",
            string_value=service.service_name,
        )
        scaling = service.auto_scale_task_count(
            min_capacity=config["min_count"], max_capacity=config["max_count"]
        )
        scaling.scale_on_cpu_utilization(
            f"{self.api_name_capitalized}ApiCpuScaling",
            target_utilization_percent=config["scaling_target_cpu_utilization"],
        )
        return service

    def create_target_group(
        self,
        env_name: str = None,
        app_vpc: ec2.IVpc = None,
        alb_listener: elbv2.IApplicationListener = None,
        service: ecs.FargateService = None,
    ):
        config = CONFIG[env_name]["alb"]
        target_group = elbv2.ApplicationTargetGroup(
            self,
            f"{self.api_name_capitalized}ApiTargetGroup",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
            vpc=app_vpc,
        )
        alb_listener.add_target_groups(
            f"{self.api_name_capitalized}ApiTargetGroup",
            conditions=[
                elbv2.ListenerCondition.path_patterns([f"/api/{self.api_name}/*"])
            ],
            target_groups=[target_group],
            priority=config["target_group_priority"],
        )
        return target_group
