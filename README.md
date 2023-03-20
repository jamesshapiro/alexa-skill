# Summary

Create an Alexa-compatible AWS Lambda function using Terraform.

# AWS + Terraform + Deploy Instructions

```
# Install lambda requirements
pip3 install --target ./lambda ask_sdk_core
pip3 install --target ./lambda openai
pip3 install --target ./lambda langchain

# Initialize terraform
terraform init

# Deploy
terraform apply
```

# Code Notes

`lambda/lambda_function.py` `language_strings.json` and `prompts.py` are the function.

Remaining files are part of requirements.txt for bundling ask-sdk-core into lambda.

# Alexa Integration

Visit the [Alexa Console](https://developer.amazon.com/alexa/console/ask) to integrate. Use the terraform output's lambda ARN as the skill's Endpoint.
