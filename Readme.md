# AWS Rekognition Messenger bot on Lambda

This serves as a simple example how to use AWS Rekognition service for bots on Messenger which run on AS Lamba instance. It is written in `python3.6` as a prototype only.


On developer's side it requires to add facebook page token as environmental variable `FB_TOKEN` and create an S3 bucket in which the incoming image is stored and then submited to `Rekognition`. It should be possible to send base64 encoded image straight from facebook's url to Rekognition, but did not work for me at the moment, so S3 is used as a workaround. For deployment, I recommende `zappa` for beginners.

## Prerequisities
- AWS account - familiarity with Lambda and S3 instances
- Lambda IAM role enabling it to use Rekognition and S3 resources
- Subscribe bot to a facebook page, use messaging token as `FB_TOKEN` env variable
- on line68 define the verification token for webhook, or use the default value to verify the webhook

- Zappa deployment returns the webhook's url