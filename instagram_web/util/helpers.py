import boto3, botocore
from app import app
import braintree

s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config["S3_KEY"],
   aws_secret_access_key=app.config["S3_SECRET"]
)

def upload_file_to_s3(file, username, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            app.config.get("S3_BUCKET"),
            "{}/{}".format(username, file.filename),
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    return "{}/{}".format(username, file.filename)

# From braintree library, create a gateway
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=app.config.get("BT_MERCHANT_ID"),
        public_key=app.config.get("BT_PUBLIC_KEY"),
        private_key=app.config.get("BT_PRIVATE_KEY")
    )
)    