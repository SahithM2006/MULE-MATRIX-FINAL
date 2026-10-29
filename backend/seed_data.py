import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import engine, Base, SessionLocal
from app.services.scenario_generator import ScenarioGenerator
from app.services.evaluation_service import EvaluationService
from app.models.entities import Account, Transaction

def main():
    print("MULE MATRIX Database Initialization...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        acc_count = db.query(Account).count()
        if acc_count > 0:
            print(f"Database already contains {acc_count} accounts and {db.query(Transaction).count()} transactions.")
        else:
            print("Generating 1,500 accounts and 30,000 synthetic transactions across 6 synthetic institutions...")
            res = ScenarioGenerator.generate_full_seeded_dataset(db, total_accounts=1500, total_transactions=30000, seed=42)
            print(f"Generated: {res}")
            
        print("Training baseline models and evaluating held-out benchmark...")
        bench = EvaluationService.run_benchmark_evaluation(db, test_seed=42)
        print("Benchmark Complete:")
        print(f"  Baseline Rule F1: {bench['rule_baseline']['f1_score']}")
        print(f"  Candidate Multi-Engine F1: {bench['candidate_detector']['f1_score']}")
        print(f"  Avg Latency: {bench['avg_latency_per_account_ms']} ms/account")
        print("Initialization finished successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    main()

