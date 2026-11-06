
import json
import logging
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALLOWED_ENVIRONMENTS = {"dev", "test"}
ALLOWED_INSTANCE_TYPES = {"t3.micro"}

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        # Support direct Lambda tests and API Gateway requests.
        if "body" in event:
            body = event["body"]

            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            data = event

        if not isinstance(data, dict):
            return response(400, {
                "message": "Request must be a JSON object"
            })
            
        # Enforce validation-only mode.
        if data.get("dry_run") is not True:
            return response(403, {
                "status": "rejected",
                "message": "Only dry_run=true is allowed",
                "instance_created": False
            })


        request_id = data.get("request_id")
        server_name = data.get("server_name")
        environment = data.get("environment")
        instance_type = data.get("instance_type")

        # Validate request fields.
        if not all(
            isinstance(value, str) and value.strip()
            for value in [
                request_id,
                server_name,
                environment,
                instance_type
            ]
        ):
            return response(400, {
                "message": "All fields are required"
            })

        if not re.fullmatch(r"RITM\d{7,}", request_id):
            return response(400, {
                "message": "Invalid ServiceNow request ID"
            })

        if not re.fullmatch(
            r"[a-zA-Z0-9-]{1,40}", server_name
        ):
            return response(400, {
                "message": "Invalid server name"
            })

        if environment not in ALLOWED_ENVIRONMENTS:
            return response(400, {
                "message": "Environment not allowed"
            })

        if instance_type not in ALLOWED_INSTANCE_TYPES:
            return response(400, {
                "message": "EC2 instance type not allowed"
            })

        logger.info(
            "Validated provisioning request: %s",
            request_id
        )

        # Phase 2: No EC2 instance is created.
        return response(200, {
            "status": "validated",
            "message": "Provisioning request validated",
            "request_id": request_id,
            "server_name": server_name,
            "environment": environment,
            "instance_type": instance_type,
            "dry_run": True,
            "instance_created": False
        })

    except (json.JSONDecodeError, UnicodeDecodeError):
        return response(400, {
            "message": "Invalid JSON request"
        })

    except Exception:
        logger.exception("Unexpected Lambda error")
        return response(500, {
            "message": "Internal server error"
        })
