import aws_cdk as core
import aws_cdk.assertions as assertions

from first_steps_abalytics.first_steps_abalytics_stack import FirstStepsAbalyticsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in first_steps_abalytics/first_steps_abalytics_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FirstStepsAbalyticsStack(app, "first-steps-abalytics")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
