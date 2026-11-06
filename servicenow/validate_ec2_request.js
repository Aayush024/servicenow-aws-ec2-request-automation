
(function execute(inputs, outputs) {

    outputs.http_status = 0;
    outputs.result_status = "error";
    outputs.result_message = "Validation was not completed";
    outputs.instance_created = false;

    try {
        var request = new sn_ws.RESTMessageV2(
            "AWS EC2 Provisioning API",
            "ValidateProvisioning"
        );

        var payload = {
            request_id: String(inputs.request_id),
            server_name: String(inputs.server_name),
            environment: String(inputs.environment),
            instance_type: String(inputs.instance_type),
            dry_run: true
        };

        request.setRequestHeader(
            "Content-Type", "application/json"
        );

        request.setRequestBody(JSON.stringify(payload));
        request.setHttpTimeout(30000);

        var response = request.execute();

        var statusCode = response.getStatusCode();
        var responseBody = response.getBody();

        outputs.http_status = statusCode;

        var result = JSON.parse(responseBody);

        var validResponse =
            statusCode === 200 &&
            result.status === "validated" &&
            result.dry_run === true &&
            result.instance_created === false &&
            result.request_id === payload.request_id;

        outputs.instance_created =
            result.instance_created === true;

        if (validResponse) {
            outputs.result_status = "validated";
            outputs.result_message =
                result.message || "Validation successful";
        } else {
            outputs.result_status = "error";
            outputs.result_message =
                "Validation failed. HTTP=" + statusCode +
                ", AWS status=" + result.status +
                ", Expected RITM=" + payload.request_id +
                ", Returned RITM=" + result.request_id +
                ", dry_run=" + result.dry_run +
                ", instance_created=" + result.instance_created;
        }

    } catch (ex) {
        outputs.result_status = "error";
        outputs.result_message =
            "AWS REST integration failed: " + ex.message;
    }

})(inputs, outputs);
