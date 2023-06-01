import logging
import time

import boto3

from crs2rss.config import settings

log = logging.getLogger(__name__)


def upload_feed(feed: str) -> None:
    filename = settings.aws.file_name

    # Create an S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws.access_key,
        aws_secret_access_key=settings.aws.secret_key,
    )

    # Upload the string as a file to the specified bucket
    s3_client.put_object(
        Body=feed,
        Bucket=settings.aws.bucket_name,
        Key=filename,
        ContentType="text/xml",
    )

    # Create a CloudFront client
    cloudfront_client = boto3.client(
        "cloudfront",
        aws_access_key_id=settings.aws.access_key,
        aws_secret_access_key=settings.aws.secret_key,
    )

    # Create an invalidation request for the file
    paths = [f"/{filename}"]
    invalidation_response = cloudfront_client.create_invalidation(
        DistributionId=settings.aws.distribution_id,
        InvalidationBatch={
            "Paths": {"Quantity": len(paths), "Items": paths},
            "CallerReference": f"{filename}-invalidation-{time.time()}",
        },
    )

    log.info("CloudFront invalidation requested for file: %s", filename)
    log.debug("Invalidation ID: %s", invalidation_response["Invalidation"]["Id"])
