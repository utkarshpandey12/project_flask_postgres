import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import pipelines
from constructs import Construct

from .api_stack import ApiStage
from .config import CONFIG


class ApiPipelineStack(cdk.Stack):
    def __init__(
        self, scope: Construct, construct_id: str, api_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.api_name = api_name
        self.api_name_capitalized = api_name.capitalize()
        repo = self.create_repo()
        pipeline = self.create_pipeline(repo=repo)
        env_names = ["dev", "stg"]
        ecr_repo = self.create_ecr_repo(env_names=env_names)
        self.perform_docker_build(
            pipeline_env_name="pipeline", pipeline=pipeline, ecr_repo=ecr_repo
        )
        for env_name in env_names:
            self.setup_env(env_name, pipeline=pipeline, ecr_repo=ecr_repo)

    def setup_env(self, env_name, *, pipeline, ecr_repo):
        self.sync_ssm_params_to_env(
            env_name=env_name, pipeline=pipeline, ecr_repo=ecr_repo
        )
        self.deploy_to_env(env_name=env_name, pipeline=pipeline)
        self.force_service_deployment_in_env(env_name=env_name, pipeline=pipeline)

    def create_repo(self) -> codecommit.Repository:
        repo = codecommit.Repository(
            self,
            f"{self.api_name_capitalized}ApiRepo",
            repository_name=f"{self.api_name}-api",
        )
        read_policy = iam.ManagedPolicy(
            self,
            f"{self.api_name_capitalized}ApiReadPolicy",
            description=f"Provides read access to {self.api_name}-api repo",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "codecommit:List*",
                            "codecommit:BatchDescribe*",
                            "codecommit:BatchGet*",
                            "codecommit:Describe*",
                            "codecommit:EvaluatePullRequestApprovalRules",
                            "codecommit:Get*",
                            "codecommit:GitPull",
                        ],
                        resources=[
                            repo.repository_arn,
                        ],
                    )
                ]
            ),
        )
        write_policy = iam.ManagedPolicy(
            self,
            f"{self.api_name_capitalized}ApiWritePolicy",
            description=f"Provides write access to {self.api_name}-api repo",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "codecommit:CreatePullRequest",
                            "codecommit:DeleteCommentContent",
                            "codecommit:GitPush",
                            "codecommit:PostComment*",
                            "codecommit:PutComment*",
                            "codecommit:UpdateComment*",
                            "codecommit:UpdatePullRequest*",
                        ],
                        resources=[
                            repo.repository_arn,
                        ],
                    )
                ]
            ),
        )
        iam.Group(
            self,
            f"{self.api_name_capitalized}ApiReadOnlyGroup",
            group_name=f"{self.api_name_capitalized}ApiReadOnlyGroup",
            managed_policies=[read_policy],
        )
        iam.Group(
            self,
            f"{self.api_name_capitalized}ApiReadWriteGroup",
            group_name=f"{self.api_name_capitalized}ApiReadWriteGroup",
            managed_policies=[read_policy, write_policy],
        )

        return repo

    def create_pipeline(
        self, *, repo: codecommit.Repository = None
    ) -> pipelines.CodePipeline:
        pipeline = pipelines.CodePipeline(
            self,
            f"{self.api_name_capitalized}ApiPipeline",
            synth=pipelines.CodeBuildStep(
                "Synth",
                input=pipelines.CodePipelineSource.code_commit(
                    repository=repo,
                    branch="main",
                ),
                install_commands=[
                    "cd cdk",
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt",
                ],
                commands=[
                    "cdk synth",
                ],
                primary_output_directory="cdk/cdk.out",
            ),
            cross_account_keys=True,
        )
        return pipeline

    def create_ecr_repo(self, env_names: list[str] = None):
        principals = []
        for env_name in env_names:
            config = CONFIG[env_name]
            principals.append(iam.AccountPrincipal(config["account"]))

        ecr_repo = ecr.Repository(self, f"{self.api_name_capitalized}ApiEcrRepo")
        ecr_repo.node.default_child.add_property_override(
            "RepositoryPolicyText",
            iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:BatchGetImage",
                            "ecr:GetDownloadUrlForLayer",
                        ],
                        effect=iam.Effect.ALLOW,
                        principals=principals,
                    )
                ],
            ).to_json(),
        )
        ecr_repo.add_lifecycle_rule(
            description="Retain only the latest 5 images", max_image_count=5
        )
        return ecr_repo

    def sync_ssm_params_to_env(
        self,
        env_name: str = None,
        pipeline: pipelines.CodePipeline = None,
        ecr_repo: ecr.Repository = None,
    ):
        config = CONFIG[env_name]
        env_name_capitalized = env_name.capitalize()

        account = config["account"]
        role_arn = f"arn:aws:iam::{account}:role/CrossAccountRoleForPipelines"

        sync_ssm_params = pipelines.CodeBuildStep(
            "SyncSsmParams",
            install_commands=[
                # Assume role
                f"ASSUMED_ROLE=$(aws sts assume-role --role-arn {role_arn} "
                f"--role-session-name sync)",
                # Export AccessKeyId
                'export AWS_ACCESS_KEY_ID=$(echo "${ASSUMED_ROLE}" | '
                'jq -r ".Credentials.AccessKeyId")',
                # Export SecretAccessKey
                'export AWS_SECRET_ACCESS_KEY=$(echo "${ASSUMED_ROLE}" | '
                'jq -r ".Credentials.SecretAccessKey")',
                # Export SessionToken
                'export AWS_SESSION_TOKEN=$(echo "${ASSUMED_ROLE}" | '
                'jq -r ".Credentials.SessionToken")',
            ],
            commands=[
                # Put SSM Param - ecr repo arn
                f"aws ssm put-parameter --name '{self.api_name}-api-ecr-repo-arn' "
                f"--value {ecr_repo.repository_arn} --type 'String' --overwrite",
                # Put SSM Param - ecr repo name
                f"aws ssm put-parameter --name '{self.api_name}-api-ecr-repo-name' "
                f"--value {ecr_repo.repository_name} --type 'String' --overwrite",
            ],
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sts:AssumeRole",
                    ],
                    resources=[
                        role_arn,
                    ],
                )
            ],
        )
        pipeline.add_wave(
            f"SyncSsmParamsTo{env_name_capitalized}", post=[sync_ssm_params]
        )

    def perform_docker_build(
        self,
        pipeline_env_name: str = None,
        pipeline: pipelines.CodePipeline = None,
        ecr_repo: ecr.Repository = None,
    ):
        config = CONFIG[pipeline_env_name]
        account = config["account"]
        region = config["region"]
        ecr_repo_name = ecr_repo.repository_name
        ecr_repo_latest_tag_uri = ecr_repo.repository_uri_for_tag(tag="latest")

        docker_build = pipelines.CodeBuildStep(
            "Build",
            build_environment=codebuild.BuildEnvironment(
                privileged=True,
            ),
            install_commands=[
                # Get docker credentials from secrets manager
                "DOCKER_CREDENTIALS=$(aws secretsmanager get-secret-value "
                "--secret-id docker-credentials --output text --query SecretString)",
                # Export docker username
                'export DOCKER_USERNAME=$(echo "${DOCKER_CREDENTIALS}" | '
                'jq -r ".username")',
                # Export docker password
                'export DOCKER_PASSWORD=$(echo "${DOCKER_CREDENTIALS}" | '
                'jq -r ".password")',
                # Login to docker
                'docker login --username "$DOCKER_USERNAME" '
                '--password "$DOCKER_PASSWORD"',
            ],
            commands=[
                "cd src",
                # Docker build
                f"docker build -f docker/Dockerfile -t {ecr_repo_name}:latest .",
                # Get ecr login and login to docker
                f"aws ecr get-login-password --region {region} | "
                f"docker login --username AWS "
                f"--password-stdin {account}.dkr.ecr.{region}.amazonaws.com",
                # Docker Tag
                f"docker tag {ecr_repo_name}:latest {ecr_repo_latest_tag_uri}",
                # Docker push
                f"docker push {ecr_repo_latest_tag_uri}",
            ],
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "secretsmanager:GetSecretValue",
                    ],
                    resources=[
                        "*",
                    ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:CompleteLayerUpload",
                        "ecr:GetAuthorizationToken",
                        "ecr:InitiateLayerUpload",
                        "ecr:PutImage",
                        "ecr:UploadLayerPart",
                    ],
                    resources=[
                        "*",
                    ],
                ),
            ],
        )
        pipeline.add_wave("Docker", post=[docker_build])

    def deploy_to_env(
        self,
        *,
        env_name: str = None,
        pipeline: pipelines.CodePipeline = None,
    ):
        config = CONFIG[env_name]
        env = cdk.Environment(account=config["account"], region=config["region"])
        env_name_capitalized = env_name.capitalize()
        stage = ApiStage(
            self,
            f"DeployTo{env_name_capitalized}",
            env=env,
            api_name=self.api_name,
            env_name=env_name,
        )
        pre = None
        if config["manual_approval_required_for_deployment"]:
            pre = [
                pipelines.ManualApprovalStep(
                    f"ApproveDeploymentTo{env_name_capitalized}",
                    comment=f"Approve deployment to {env_name_capitalized}",
                )
            ]
        pipeline.add_stage(stage, pre=pre)

    def force_service_deployment_in_env(
        self,
        env_name: str = None,
        pipeline: pipelines.CodePipeline = None,
    ):
        config = CONFIG[env_name]
        env_name_capitalized = env_name.capitalize()

        account = config["account"]
        role_arn = f"arn:aws:iam::{account}:role/CrossAccountRoleForPipelines"

        force_service_deployment = pipelines.CodeBuildStep(
            "ForceServiceDeployment",
            install_commands=[
                # Assume role
                f"ASSUMED_ROLE=$(aws sts assume-role --role-arn {role_arn} "
                f"--role-session-name service_force_deploy)",
                # Export AccessKeyId
                'export AWS_ACCESS_KEY_ID=$(echo "${ASSUMED_ROLE}" | '
                'jq -r ".Credentials.AccessKeyId")',
                # Export SecretAccessKey
                'export AWS_SECRET_ACCESS_KEY=$(echo "${ASSUMED_ROLE}" | '
                'jq -r ".Credentials.SecretAccessKey")',
                # Export SessionToken
                'export AWS_SESSION_TOKEN=$(echo "${ASSUMED_ROLE}" | '
                'jq -r ".Credentials.SessionToken")',
            ],
            commands=[
                # Export ECS Cluster Name
                "export CLUSTER_NAME=$(aws ssm get-parameter "
                "--name 'app-ecs-cluster-name' --output text "
                "--query Parameter.Value)",
                # Export ECS Service Name
                f"export SERVICE_NAME=$(aws ssm get-parameter "
                f"--name '{self.api_name}-api-service-name' --output text "
                f"--query Parameter.Value)",
                # Update Service
                "aws ecs update-service --cluster $CLUSTER_NAME --service "
                "$SERVICE_NAME --force-new-deployment",
            ],
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sts:AssumeRole",
                    ],
                    resources=[
                        role_arn,
                    ],
                )
            ],
        )
        pipeline.add_wave(
            f"ForceServiceDeploymentIn{env_name_capitalized}",
            post=[force_service_deployment],
        )
