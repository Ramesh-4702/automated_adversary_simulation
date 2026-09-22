#!/usr/bin/env python3
import sys
import yaml
import argparse
from datetime import datetime
from engine.runner import TestbedRunner
from engine.validator import DetectionValidator

CONFIG_PATH = "config/techniques.yaml"

def main():
    parser = argparse.ArgumentParser(description="Automated Adversary Simulation ")
    parser.add_argument("--config", default=CONFIG_PATH, help="Path to YAML config")
    parser.add_argument("--json-out", help="Export JSON summary report")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        techniques = yaml.safe_load(f).get("techniques", [])

    runner = TestbedRunner()
    validator = DetectionValidator()

    try:
        print("[*] Deploying ephemeral Docker container...")
        runner.setup_environment()

        print("[*] Running MITRE ATT&CK simulation payloads...")
        results = []

        for tech in techniques:
            runner.execute_payload(tech["payload"])
            logs = validator.fetch_container_logs()
            detected = validator.validate_technique(tech, logs)
            results.append((tech["id"], tech["name"], tech["tactic"], "PASSED" if detected else "BLIND SPOT"))

        print("\n" + "="*70)
        print("                          SIMULATION REPORT")
        print("="*70)
        for r in results:
            print(f"{r[0]:<12} {r[1]:<30} {r[2]:<18} {r[3]}")
        print("="*70)

    finally:
        print("[*] Tearing down test bed...")
        runner.teardown_environment()

if __name__ == "__main__":
    main()
