import setuptools


with open("README.md") as fp:
    long_description = fp.read()

cdk_version = "1.62.0"

setuptools.setup(
    name="cdk",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "cdk"},
    packages=setuptools.find_packages(where="cdk"),

    install_requires=[
        "aws-cdk.core==" + cdk_version,
        "aws-cdk.aws-s3==" + cdk_version,
        "aws-cdk.aws-ec2==" + cdk_version,
        "aws-cdk.aws-lambda==" + cdk_version,
        "aws-cdk.aws-lambda==" + cdk_version,
        "aws_cdk.aws_appsync==" + cdk_version,
        "aws_cdk.aws_pinpoint==" + cdk_version,
        "aws_cdk.aws_elasticsearch==" + cdk_version,
        "aws_cdk.aws_kinesisfirehose==" + cdk_version,
        "aws_cdk.aws_cloudfront==" + cdk_version,
        "aws-cdk.aws-secretsmanager==" + cdk_version,
        "aws-cdk.aws-rds==" + cdk_version,
        "aws-cdk.aws-pinpoint==" + cdk_version,
        "aws-cdk.aws_cognito==" + cdk_version,
        "aws-cdk.aws_cloudwatch==" + cdk_version,
        "aws-cdk.aws_logs==" + cdk_version,
        "aws-cdk.aws_dynamodb==" + cdk_version
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
