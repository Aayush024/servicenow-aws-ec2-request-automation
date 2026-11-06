
import os
import json
import hmac
import base64
import boto3

from botocore.exceptions import ClientError

secrets_client = boto3.client("secretsmanager")

SECRET_NAME = os.environ["SECRET_NAME"]


def lambda_handler(event, context):
    try:
        headers = event.get("headers") or {}

        authorization = next(
            (
                value for key, value in headers.items()
                if key.lower() == "authorization"
            ),
            ""
        )

        if not authorization.startswith("Basic "):
            return {"isAuthorized": False}

        encoded = authorization[6:].strip()

        decoded = base64.b64decode(
            encoded, validate=True
        ).decode("utf-8")

        username, separator, token = decoded.partition(":")

        if not separator or not token:
            return {"isAuthorized": False}

        result = secrets_client.get_secret_value(
            SecretId=SECRET_NAME
        )

        stored = json.loads(result["SecretString"])

        username_valid = hmac.compare_digest(
            username.encode("utf-8"),
            stored["username"].encode("utf-8")
        )

        token_valid = hmac.compare_digest(
            token.encode("utf-8"),
            stored["token"].encode("utf-8")
        )

        return {
            "isAuthorized": username_valid and token_valid
        }

    except (
        ValueError,
        UnicodeError,
        KeyError,
        TypeError
    ):
        return {"isAuthorized": False}

    except ClientError:
        # Do not expose secret details in logs.
        raise
