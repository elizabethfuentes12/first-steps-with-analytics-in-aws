# AGENTS.md

## What this is
CDK (Python) demo of a small data-analytics pipeline on AWS: a file dropped in an S3 bucket triggers a Lambda that moves it to a raw prefix and starts a Glue crawler; an EventBridge rule on crawler completion triggers a second Lambda. Tables land in the Glue Data Catalog for Athena/QuickSight. Companion to the Spanish blog post in `README.md`.

## Structure
- `first-steps-analytics/app.py` – CDK entrypoint (`AwsFirstStepsStack`, region `us-east-1`).
- `first-steps-analytics/first_steps_analytics/first_steps_analytics_stack.py` – S3 bucket + notification, Glue database (`aws_glue_alpha`), `CfnCrawler`, IAM role, two Lambdas, EventBridge rule.
- `first-steps-analytics/lambdas/process_new_file/lambda_function.py` – copies the new object and starts the crawler.
- `first-steps-analytics/lambdas/post_crawler/lambda_function.py` – runs after the crawler finishes.
- `imagen/` – README images.

## Commands
```bash
cd first-steps-analytics
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk synth      # CDK CLI: npm install -g aws-cdk
cdk deploy     # creates real resources (S3, Lambda, Glue, IAM, EventBridge)
```

## Dependencies
- `aws-cdk-lib==2.277.0`, `aws-cdk.aws-glue-alpha==2.274.0a0`, `constructs>=10,<11`.
- Lambda runtime **Python 3.13**; handlers use only the stdlib + `boto3` from the runtime.

## Conventions / gotchas
- `aws_glue_alpha.Database` and `DataFormat` props emit deprecation warnings on synth (alpha API); they still synthesize. Migrating to the stable `aws_glue.CfnDatabase` is a possible future change.
- IAM role name `CrawlerDemoCDK` is hardcoded (one stack per account).

## Recent changes
- 2026-11: Lambda runtime `python3.8` (deprecated 2024-10-14) -> `python3.13`; `aws-cdk-lib` 2.19.0 -> 2.277.0; glue-alpha pinned to 2.274.0a0. Verified with `cdk synth` (3 functions render `python3.13`) and by importing both handlers under Python 3.13. Not deployed.
