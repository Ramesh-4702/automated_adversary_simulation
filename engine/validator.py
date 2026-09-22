import re
import subprocess

class DetectionValidator:
    def __init__(self, container_name="ephemeral_target"):
        self.container_name = container_name

    def fetch_container_logs(self):
        #Fetches telemetry logs captured inside the target container.
        result = subprocess.run(
            ["docker", "exec", self.container_name, "cat", "/var/log/adversary_execution.log"],
            capture_output=True,
            text=True
        )
        return result.stdout

    def validate_technique(self, technique, log_stream):
        #Asserts whether expected log regex exists in captured telemetry.
        pattern = technique.get("expected_log_regex", "")
        if not pattern:
            return False
        return bool(re.search(pattern, log_stream, re.IGNORECASE))
