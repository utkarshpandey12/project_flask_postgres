import aws_cdk as core
import aws_cdk.assertions as assertions
from api.api_pipeline_stack import ApiPipelineStack


def test_sqs_queue_created():
    app = core.App()
    stack = ApiPipelineStack(app, "admin-api")
    assertions.Template.from_stack(stack)
