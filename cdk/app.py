#!/usr/bin/env python3
import aws_cdk as cdk
from api.api_pipeline_stack import ApiPipelineStack
from api.config import CONFIG

app = cdk.App()
config = CONFIG["pipeline"]
pipeline_env = cdk.Environment(account=config["account"], region=config["region"])
ApiPipelineStack(app, "AdminApiPipelineStack", api_name="admin", env=pipeline_env)
app.synth()
