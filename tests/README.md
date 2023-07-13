# Testing

I know of three ways to test aws-org-tree without using a real AWS account.

1. [Moto](https://github.com/spulec/moto) has an Organizations backend. Its implementation is incomplete. It doesn't behave correctly for simple edges cases such as not running in an organization.

2. [Stubber](https://botocore.amazonaws.com/v1/documentation/api/latest/reference/stubber.html) gives me control of the edge cases but is inflexible. It forces an expected order of API operations on the implementation. There are many ways to describe an organization. I don't want to constrain the implementation, but I do know the output for a given organizational state.

3. [unittest.mock.patch](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch) gives complete control and flexibility, but I need to maintain my own test abtractions. It may be the best option when the other options don't do what I need.

Ideally I'd use Moto for everything because it produces the most readable test code. The long-term solution is to improve Moto's Organizations backend, but that will take some time. Until then, I'll use hybrid methods to get good enough test coverage.

## Research

Use [Snyk](https://snyk.io/advisor/python/botocore/functions/botocore.stub.Stubber) to search GitHub for use of Stubber.[^gh-dire] Its own documentation is okay, but I can learn more from real-world use.

* Chalice uses Stubber as of 2023-07-13. Read the docs on [testing](https://github.com/aws/chalice/blob/79838b02dc330cfe549823899d2662ded0538015/docs/source/topics/testing.rst) and [contributing](https://github.com/aws/chalice/blob/79838b02dc330cfe549823899d2662ded0538015/CONTRIBUTING.rst) for examples.
* Cloudformation CLI [used Stubber until 2019](https://github.com/aws-cloudformation/cloudformation-cli/pull/217/). It's unclear what it was replaced with.
* [onicagroup/runway](https://github.com/onicagroup/runway/blob/b60cc535e2eaa2a55a5c89c18cefd0662244967f/tests/cfngin/test_context.py#L406)
* [mozilla/telemetry-analysis-service](https://github.com/mozilla/telemetry-analysis-service/blob/b4b0c8dab3ff9a11648eeb177952b64ecfe2ded4/tests/jobs/test_provisioners.py#L168)
* [aws/aws-secretsmanager-caching-python](https://github.com/aws/aws-secretsmanager-caching-python/blob/46e1b585b089fc1a857a649031d3bb2cf4abeb3c/test/unit/test_decorators.py#L29)
* [boto/botocore](https://github.com/boto/botocore/blob/c2f18c15ca601d5cfdd6767535a96de9b13f1543/tests/unit/test_client.py#L1494)
* [awslabs/aws-sam-cli](https://github.com/awslabs/aws-sam-cli/blob/4f2c345c5e415ec443cb55b82dd7cbb7b0ba2ad6/tests/unit/lib/bootstrap/test_bootstrap.py#L17)
* [mozilla-iam/cis](https://github.com/mozilla-iam/cis/blob/8d782ed7f6c96125df2d5a4033ad2027c9f4b5e5/python-modules/cis_identity_vault/cis_identity_vault/vault.py#L41)

Articles that demonstrate and compare different methods.

* [Comparison of Moto, Stubber, and PySpark](https://github.com/paramraghavan/python-pytest)
* [Comparison of Moto, Stubber, and LocalStack](https://www.sanjaysiddhanti.com/2020/04/08/s3testing/)
* An [article](https://xebia.com/blog/how-to-create-python-unit-tests-for-aws-using-the-botocore-stubber/) showing how to use the ([PyPI](https://pypi.org/project/botocore-stubber-recorder/), [GitHub](https://github.com/binxio/botocore-stubber-recorder)) to record an AWS API conversation. Like VCR for Ruby and Python.
* [Example to patch _make_api_call](https://stackoverflow.com/questions/37143597/mocking-boto3-s3-client-method-python)

[^gh-dire]: For this use case Snyk's index gives better results that GitHub's own.
