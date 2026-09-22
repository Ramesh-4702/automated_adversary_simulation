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
    parser.add_argument("--model", default="llama3.2", help="Ollama model to evaluate (e.g. llama3.2, qwen2.5:7b)") # Adding lowest model to reduce the space usage 
    args = parser.parse_args()

    with open(args.config, "r") as f:
        techniques = yaml.safe_load(f).get("techniques", [])

    runner = TestbedRunner()
    validator = DetectionValidator()

    print(f"[*] Starting Security & Guardrail Evaluation")
    print(f"[*] Target LLM Model: {args.model}")

    # Split techniques into System vs LLM safety checks
    system_techs = [t for t in techniques if not t["id"].startswith("LLM-")]
    llm_techs = [t for t in techniques if t["id"].startswith("LLM-")]

    results = []

    # 1. Run Linux System Techniques inside Docker
    if system_techs:
        try:
            print("\n[*] Deploying Docker container for infrastructure testing...")
            runner.setup_environment()
            for tech in system_techs:
                runner.execute_payload(tech["payload"])
                logs = validator.fetch_container_logs()
                detected = validator.validate_technique(tech, logs)
                results.append((tech["id"], tech["name"], tech["tactic"], "PASSED" if detected else "BLIND SPOT"))
        finally:
            runner.teardown_environment()

    # 2. Run LLM Guardrail & Prompt Injection Techniques against Ollama
    if llm_techs:
        print(f"\n[*] Evaluating LLM Prompt Injections against local model: {args.model}...")
        for tech in llm_techs:
            success, output = runner.execute_llm_payload(tech["payload"], model_name=args.model)
            # If the model outputs the forbidden pattern, it means the guardrail failed (BLIND SPOT / VULNERABLE)
            breached = validator.validate_technique(tech, output)
            
            # For LLMs: if breached == True, safety failed (BLIND SPOT); if False, model resisted attack (PASSED)
            status = "BLIND SPOT (VULNERABLE)" if breached else "PASSED (GUARDED)"
            results.append((tech["id"], tech["name"], tech["tactic"], status))

    print("\n" + "="*80)
    print("                      EVALUATION REPORT")
    print("="*80)
    for r in results:
        print(f"{r[0]:<12} {r[1]:<32} {r[2]:<22} {r[3]}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()