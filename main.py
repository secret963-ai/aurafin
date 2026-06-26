"""
AuraFin: Financial Resilience & Employment Accelerator
Entry point — runs the full Mediation-to-Work pipeline.
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.coordinator import run_pipeline

load_dotenv()

if __name__ == "__main__":
    # Demo: run pipeline for a sample consumer
    consumer_id = os.getenv("DEMO_CONSUMER_ID", "CONSUMER-001")
    print(f"\n{'='*60}")
    print("  AuraFin: Financial Resilience & Employment Accelerator")
    print(f"{'='*60}\n")
    asyncio.run(run_pipeline(consumer_id))
