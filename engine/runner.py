import time
import subprocess

CONTAINER_NAME = "ephemeral_target"
IMAGE_NAME = "target_bed"

class TestbedRunner:
    def __init__(self, container_name=CONTAINER_NAME, image_name=IMAGE_NAME):
        self.container_name = container_name
        self.image_name = image_name

    def setup_environment(self, verbose=False):
        #setup an ephemeral Docker test bed.
        subprocess.run(
            ["docker", "build", "-t", self.image_name, "-f", "dockerfile.target", "."],
            stdout=subprocess.DEVNULL if not verbose else None,
            stderr=subprocess.DEVNULL if not verbose else None,
            check=True
        )
        self.teardown_environment(verbose=False)
        subprocess.run(
            ["docker", "run", "-d", "--name", self.container_name, self.image_name],
            stdout=subprocess.DEVNULL if not verbose else None,
            stderr=subprocess.DEVNULL if not verbose else None,
            check=True
        )
        time.sleep(2)

    def execute_payload(self, payload):
        #Executes a payload inside the container and mirrors output to execution log.
        exec_cmd = f"{payload} && echo '[AUDIT] Executed: {payload}' >> /var/log/adversary_execution.log"
        result = subprocess.run(
            ["docker", "exec", self.container_name, "bash", "-c", exec_cmd],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr

    def teardown_environment(self, verbose=False):
       # close when execution complete 
        subprocess.run(
            ["docker", "rm", "-f", self.container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
