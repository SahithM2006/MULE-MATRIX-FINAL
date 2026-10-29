import random
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models.entities import (
    SyntheticInstitution, Account, Transaction, ScenarioDefinition,
    ScenarioRun, TokenLineage, Alert, FeatureSnapshot, utc_now
)
from app.algorithms.lineage_verifier import LineageVerifier
from app.algorithms.feature_extractor import FeatureExtractor
from app.services.graph_service import GraphService

class ScenarioGenerator:
    """
    Synthetic Multi-Bank Transaction Generator
    Generates deterministic, highly realistic financial networks including:
    - Background legitimate retail and corporate banking
    - Suspicious mule patterns (rapid pass-through, smurfing, layering, mule rings, cross-bank split-merge)
    - Legitimate lookalikes (merchant fan-in, corporate payroll fan-out)
    - Cryptographic token-lineage (e₹ CBDC tracking with tamper simulation)
    """

    INSTITUTIONS = [
        {"id": "inst_apex", "code": "APEX001", "name": "Apex Reserve Bank", "swift": "APEXINBB", "tier": "STANDARD"},
        {"id": "inst_continental", "code": "CONT002", "name": "Continental Commercial Bank", "swift": "CONTINBB", "tier": "STANDARD"},
        {"id": "inst_zenith", "code": "ZENI003", "name": "Zenith Digital NeoBank", "swift": "ZENIINBB", "tier": "ELEVATED"},
        {"id": "inst_vanguard", "code": "VANG004", "name": "Vanguard Cooperative Union", "swift": "VANGINBB", "tier": "STANDARD"},
        {"id": "inst_indus", "code": "INDU005", "name": "Indus Premier Bank", "swift": "INDUINBB", "tier": "STANDARD"},
        {"id": "inst_neopay", "code": "NEOP006", "name": "NeoPay Settlement Gateway", "swift": "NEOPINBB", "tier": "HIGH_RISK"}
    ]

    FIRST_NAMES = ["Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Ananya", "Sanjay", "Neha", "Kabir", "Pooja", "Rahul", "Meera", "Arjun", "Kavita", "Deepak", "Sneha", "Karan", "Divya", "Amit", "Sunita"]
    LAST_NAMES = ["Sharma", "Verma", "Patel", "Mehta", "Reddy", "Nair", "Iyer", "Gupta", "Malhotra", "Kapoor", "Joshi", "Chopra", "Bose", "Das", "Rao", "Menon", "Saxena", "Bhat", "Deshmukh", "Singhania"]
    
    @classmethod
    def seed_institutions(cls, db: Session):
        for data in cls.INSTITUTIONS:
            inst = db.query(SyntheticInstitution).filter_by(id=data["id"]).first()
            if not inst:
                inst = SyntheticInstitution(
                    id=data["id"],
                    routing_code=data["code"],
                    name=data["name"],
                    swift_bic=data["swift"],
                    risk_tier=data["tier"],
                    country="IN"
                )
                db.add(inst)
        db.commit()

    @classmethod
    def generate_full_seeded_dataset(
        cls,
        db: Session,
        total_accounts: int = 1500,
        total_transactions: int = 30000,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Seeds standard large dataset if not already present.
        """
        cls.seed_institutions(db)
        existing_accs = db.query(Account).count()
        if existing_accs >= total_accounts:
            return {"status": "ALREADY_SEEDED", "accounts": existing_accs, "transactions": db.query(Transaction).count()}

        random.seed(seed)
        start_time = datetime(2026, 10, 15, 8, 0, 0, tzinfo=timezone.utc)
        
        # 1. Create Accounts
        inst_ids = [inst["id"] for inst in cls.INSTITUTIONS]
        accounts = []
        
        # Normal retail accounts
        for i in range(total_accounts - 120):
            fn = random.choice(cls.FIRST_NAMES)
            ln = random.choice(cls.LAST_NAMES)
            acc_id = f"acc_{i+1:05d}"
            acc_num = f"{random.choice(['10', '20', '30', '40'])}{i+1:08d}"
            acc = Account(
                id=acc_id,
                institution_id=random.choice(inst_ids),
                account_number=acc_num,
                account_type=random.choice(["CHECKING", "SAVINGS", "DIGITAL_WALLET"]),
                holder_name=f"{fn} {ln}",
                balance=round(random.uniform(5000.0, 250000.0), 2),
                status="ACTIVE",
                is_mule=False,
                mule_role="LEGITIMATE",
                created_at=start_time - timedelta(days=random.randint(30, 365))
            )
            accounts.append(acc)

        # Designated Merchants
        merchant_accs = []
        for i in range(20):
            acc_id = f"acc_merch_{i+1:03d}"
            acc = Account(
                id=acc_id,
                institution_id=random.choice(inst_ids),
                account_number=f"88{i+1:08d}",
                account_type="MERCHANT",
                holder_name=f"Merchant Enterprise {chr(65+i)} Retail",
                balance=round(random.uniform(100000.0, 2000000.0), 2),
                status="ACTIVE",
                is_mule=False,
                mule_role="LEGITIMATE",
                created_at=start_time - timedelta(days=400)
            )
            accounts.append(acc)
            merchant_accs.append(acc)

        # Designated Corporate Payrolls
        corporate_accs = []
        for i in range(10):
            acc_id = f"acc_corp_{i+1:03d}"
            acc = Account(
                id=acc_id,
                institution_id=random.choice(inst_ids),
                account_number=f"99{i+1:08d}",
                account_type="CORPORATE",
                holder_name=f"Global Technologies Group {i+1} Corp",
                balance=round(random.uniform(5000000.0, 25000000.0), 2),
                status="ACTIVE",
                is_mule=False,
                mule_role="LEGITIMATE",
                created_at=start_time - timedelta(days=500)
            )
            accounts.append(acc)
            corporate_accs.append(acc)

        # Off-Ramp Terminals (Crypto / ATM)
        offramp_accs = []
        for i in range(15):
            acc_id = f"acc_offramp_{i+1:03d}"
            acc = Account(
                id=acc_id,
                institution_id="inst_neopay",
                account_number=f"77{i+1:08d}",
                account_type="CRYPTO_OFFRAMP",
                holder_name=f"BitGateway Vault {i+1} Settlement",
                balance=round(random.uniform(50000.0, 500000.0), 2),
                status="ACTIVE",
                is_mule=False,
                mule_role="CASHOUT",
                created_at=start_time - timedelta(days=200)
            )
            accounts.append(acc)
            offramp_accs.append(acc)

        # Suspicious Mule Rings & Bridges
        mule_accs = []
        for i in range(75):
            acc_id = f"acc_mule_{i+1:03d}"
            acc = Account(
                id=acc_id,
                institution_id=random.choice(inst_ids),
                account_number=f"55{i+1:08d}",
                account_type="CHECKING",
                holder_name=f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)} (Syndicate Node {i+1})",
                balance=round(random.uniform(1000.0, 30000.0), 2),
                status="ACTIVE",
                is_mule=True,
                mule_role=random.choice(["SMURF", "LAYER", "BRIDGE", "ORIGIN"]),
                created_at=start_time - timedelta(days=random.randint(10, 45))
            )
            accounts.append(acc)
            mule_accs.append(acc)

        # Bulk save accounts
        db.bulk_save_objects(accounts)
        db.commit()

        # 2. Generate Transactions
        all_acc_ids = [a.id for a in accounts]
        retail_ids = [a.id for a in accounts if not a.is_mule and a.account_type in ("CHECKING", "SAVINGS", "DIGITAL_WALLET")]
        
        transactions = []
        tx_count = 0
        current_time = start_time

        # A. Background legitimate transfers (~25,000 txs)
        channels = ["UPI", "IMPS", "NEFT", "RTGS"]
        for _ in range(total_transactions - 5000):
            src = random.choice(retail_ids)
            dst = random.choice(retail_ids)
            while dst == src:
                dst = random.choice(retail_ids)
                
            tx_time = start_time + timedelta(
                days=random.randint(0, 13),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            amt = round(random.lognormvariate(7.0, 1.2), 2)  # Log-normal distribution of consumer payments
            amt = max(50.0, min(150000.0, amt))
            
            tx_id = f"tx_bg_{tx_count:06d}"
            tx_hash = hashlib.sha256(f"{tx_id}{src}{dst}{amt}{tx_time}".encode()).hexdigest()
            
            transactions.append(Transaction(
                id=tx_id,
                tx_hash=tx_hash,
                scenario_id=None,
                source_account_id=src,
                dest_account_id=dst,
                amount=amt,
                currency="INR",
                timestamp=tx_time,
                status="SETTLED",
                channel=random.choice(channels),
                description=f"Consumer Payment / P2P Settlement",
                has_token_lineage=False
            ))
            tx_count += 1

        # B. Corporate Payroll Fan-Outs (Legitimate lookalike)
        for corp in corporate_accs:
            payroll_date = start_time + timedelta(days=5, hours=9)
            recipients = random.sample(retail_ids, k=40)
            for r in recipients:
                amt = round(random.uniform(45000.0, 120000.0), 2)
                tx_id = f"tx_pay_{tx_count:06d}"
                tx_hash = hashlib.sha256(f"{tx_id}{corp.id}{r}{amt}{payroll_date}".encode()).hexdigest()
                transactions.append(Transaction(
                    id=tx_id,
                    tx_hash=tx_hash,
                    scenario_id=None,
                    source_account_id=corp.id,
                    dest_account_id=r,
                    amount=amt,
                    currency="INR",
                    timestamp=payroll_date + timedelta(seconds=random.randint(1, 300)),
                    status="SETTLED",
                    channel="NEFT",
                    description=f"Corporate Payroll Salary Disbursal",
                    has_token_lineage=False
                ))
                tx_count += 1

        # C. Merchant Fan-In (Legitimate lookalike)
        for merch in merchant_accs:
            for _ in range(60):
                customer = random.choice(retail_ids)
                t_time = start_time + timedelta(days=random.randint(1, 10), hours=random.randint(10, 21), minutes=random.randint(0, 59))
                amt = round(random.uniform(250.0, 8500.0), 2)
                tx_id = f"tx_merch_{tx_count:06d}"
                tx_hash = hashlib.sha256(f"{tx_id}{customer}{merch.id}{amt}{t_time}".encode()).hexdigest()
                transactions.append(Transaction(
                    id=tx_id,
                    tx_hash=tx_hash,
                    scenario_id=None,
                    source_account_id=customer,
                    dest_account_id=merch.id,
                    amount=amt,
                    currency="INR",
                    timestamp=t_time,
                    status="SETTLED",
                    channel="UPI",
                    description=f"POS Merchant Payment Retail Purchase",
                    has_token_lineage=False
                ))
                tx_count += 1

        # Bulk save initial transactions
        db.bulk_save_objects(transactions)
        db.commit()

        # D. Inject Canonical Hero Mule Scenarios
        cls.inject_rapid_passthrough_scenario(db, seed=42)
        cls.inject_smurfing_scenario(db, seed=43)
        cls.inject_mule_ring_scenario(db, seed=44)
        cls.inject_layering_chain_scenario(db, seed=45)
        cls.inject_cross_bank_split_merge_scenario(db, seed=46)

        # Invalidate graph cache
        GraphService.invalidate_cache()
        
        return {
            "status": "SEEDED_SUCCESS",
            "accounts_count": db.query(Account).count(),
            "transactions_count": db.query(Transaction).count()
        }

    @classmethod
    def inject_rapid_passthrough_scenario(cls, db: Session, seed: int = 101) -> ScenarioDefinition:
        """
        Scenario 1: Rapid Pass-Through Conduit
        Victim/Origin -> Intermediate Mule Account -> Multiple Cashout Destinations in < 45 minutes
        Pass-through ratio > 95%
        """
        random.seed(seed)
        scen_id = f"scen_rapid_passthrough_{seed}"
        scen = db.query(ScenarioDefinition).filter_by(id=scen_id).first()
        if scen:
            return scen

        scen = ScenarioDefinition(
            id=scen_id,
            name="Rapid Pass-Through Conduit Alpha",
            scenario_type="RAPID_PASSTHROUGH",
            description="High-velocity pass-through where 450,000 INR enters an intermediate account and is dissipated across 3 destinations within 32 minutes.",
            seed=seed
        )
        db.add(scen)
        db.commit()

        base_time = datetime(2026, 10, 28, 14, 15, 0, tzinfo=timezone.utc)
        
        # Select or create nodes
        origin_acc = db.query(Account).filter_by(id="acc_00010").first()
        mule_acc = db.query(Account).filter_by(id="acc_mule_001").first()
        offramp_acc = db.query(Account).filter_by(id="acc_offramp_001").first()
        dest2 = db.query(Account).filter_by(id="acc_mule_002").first()
        dest3 = db.query(Account).filter_by(id="acc_00025").first()
        
        mule_acc.is_mule = True
        mule_acc.mule_role = "BRIDGE"
        
        # Incoming large transfer
        tx1 = Transaction(
            id=f"tx_rpt_{seed}_in1",
            tx_hash=hashlib.sha256(f"tx_rpt_{seed}_in1".encode()).hexdigest(),
            scenario_id=scen.id,
            source_account_id=origin_acc.id,
            dest_account_id=mule_acc.id,
            amount=450000.0,
            currency="INR",
            timestamp=base_time,
            status="SETTLED",
            channel="RTGS",
            description="Urgent Loan Inward Transfer",
            has_token_lineage=True
        )
        db.add(tx1)
        
        # Outgoing rapid dispersals (12m, 20m, 32m later)
        out_amounts = [200000.0, 150000.0, 95000.0]
        out_dests = [offramp_acc.id, dest2.id, dest3.id]
        
        for idx, (amt, dst_id) in enumerate(zip(out_amounts, out_dests)):
            tx_out = Transaction(
                id=f"tx_rpt_{seed}_out_{idx+1}",
                tx_hash=hashlib.sha256(f"tx_rpt_{seed}_out_{idx+1}".encode()).hexdigest(),
                scenario_id=scen.id,
                source_account_id=mule_acc.id,
                dest_account_id=dst_id,
                amount=amt,
                currency="INR",
                timestamp=base_time + timedelta(minutes=10 * (idx + 1) + 2),
                status="SETTLED",
                channel="IMPS",
                description=f"Rapid P2P Dispersal Hop {idx+1}",
                has_token_lineage=True
            )
            db.add(tx_out)

        # Cryptographic Token Lineage for this flow (e₹ token track)
        token_id = f"eINR_TOKEN_{seed}_9921"
        lineage_events = [
            (0, tx1.id, origin_acc.id, mule_acc.id, 450000.0),
            (1, f"tx_rpt_{seed}_out_1", mule_acc.id, offramp_acc.id, 200000.0),
        ]
        prev_hash = LineageVerifier.GENESIS_PREV_HASH
        for seq, t_id, f_id, to_id, amt in lineage_events:
            payload = {
                "token_id": token_id,
                "event_seq": seq,
                "tx_id": t_id,
                "from_account_id": f_id,
                "to_account_id": to_id,
                "amount": amt,
                "timestamp": base_time.isoformat()
            }
            curr_hash = LineageVerifier.compute_event_hash(prev_hash, payload)
            lin = TokenLineage(
                id=f"lin_{token_id}_{seq}",
                token_id=token_id,
                event_seq=seq,
                tx_id=t_id,
                from_account_id=f_id,
                to_account_id=to_id,
                amount=amt,
                previous_hash=prev_hash,
                current_hash=curr_hash,
                payload_json=LineageVerifier.canonical_serialize(payload),
                is_valid=True
            )
            db.add(lin)
            prev_hash = curr_hash

        # Add High Severity Alert
        alert = Alert(
            id=f"alt_rpt_{seed}",
            account_id=mule_acc.id,
            transaction_id=tx1.id,
            severity="CRITICAL",
            alert_type="RAPID_PASSTHROUGH",
            title="Rapid Pass-Through Conduit Detected",
            description=f"Account {mule_acc.account_number} received 450,000 INR and evacuated 98.8% (445,000 INR) across 3 destinations within 32 minutes.",
            status="OPEN"
        )
        db.add(alert)
        db.commit()
        return scen

    @classmethod
    def inject_smurfing_scenario(cls, db: Session, seed: int = 102) -> ScenarioDefinition:
        """
        Scenario 2: Structured Smurfing (Fan-In)
        6 smurf accounts deposit sub-50k INR into a central collector mule within 4 hours,
        which consolidates and sends to an off-ramp.
        """
        random.seed(seed)
        scen_id = f"scen_smurf_{seed}"
        scen = db.query(ScenarioDefinition).filter_by(id=scen_id).first()
        if scen:
            return scen

        scen = ScenarioDefinition(
            id=scen_id,
            name="Structured Smurfing Syndicate Beta",
            scenario_type="SMURFING_FANIN",
            description="Six smurf accounts transfer structured amounts below reporting limits to a mule collector, followed by consolidated exit.",
            seed=seed
        )
        db.add(scen)
        db.commit()

        base_time = datetime(2026, 10, 27, 9, 30, 0, tzinfo=timezone.utc)
        collector_acc = db.query(Account).filter_by(id="acc_mule_010").first()
        offramp_acc = db.query(Account).filter_by(id="acc_offramp_002").first()
        
        collector_acc.is_mule = True
        collector_acc.mule_role = "LAYER"

        total_collected = 0.0
        smurf_amounts = [48500.0, 49200.0, 47800.0, 49900.0, 48000.0, 49500.0]
        
        for idx, amt in enumerate(smurf_amounts):
            smurf_acc = db.query(Account).filter_by(id=f"acc_mule_{11+idx:03d}").first()
            smurf_acc.is_mule = True
            smurf_acc.mule_role = "SMURF"
            t_tx = base_time + timedelta(minutes=25 * idx + 5)
            
            tx = Transaction(
                id=f"tx_smurf_{seed}_{idx+1}",
                tx_hash=hashlib.sha256(f"tx_smurf_{seed}_{idx+1}".encode()).hexdigest(),
                scenario_id=scen.id,
                source_account_id=smurf_acc.id,
                dest_account_id=collector_acc.id,
                amount=amt,
                currency="INR",
                timestamp=t_tx,
                status="SETTLED",
                channel="UPI",
                description=f"Structured UPI Deposit {idx+1}",
                has_token_lineage=False
            )
            db.add(tx)
            total_collected += amt

        # Consolidated exit transfer
        tx_exit = Transaction(
            id=f"tx_smurf_{seed}_exit",
            tx_hash=hashlib.sha256(f"tx_smurf_{seed}_exit".encode()).hexdigest(),
            scenario_id=scen.id,
            source_account_id=collector_acc.id,
            dest_account_id=offramp_acc.id,
            amount=total_collected - 2000.0,  # leaves minor commission
            currency="INR",
            timestamp=base_time + timedelta(hours=3, minutes=45),
            status="SETTLED",
            channel="RTGS",
            description="Consolidated Syndicate Settlement Exit",
            has_token_lineage=False
        )
        db.add(tx_exit)

        alert = Alert(
            id=f"alt_smurf_{seed}",
            account_id=collector_acc.id,
            transaction_id=tx_exit.id,
            severity="HIGH",
            alert_type="SMURFING_FANIN",
            title="Structured Smurfing Consolidation Alert",
            description=f"Collector mule {collector_acc.account_number} gathered {total_collected:,.2f} INR from 6 distinct senders under reporting threshold and discharged funds.",
            status="OPEN"
        )
        db.add(alert)
        db.commit()
        return scen

    @classmethod
    def inject_mule_ring_scenario(cls, db: Session, seed: int = 103) -> ScenarioDefinition:
        """
        Scenario 3: Circular Mule Ring
        Accounts A -> B -> C -> D -> A circulate funds in cycles to inflate turnover
        and obscure money trail.
        """
        random.seed(seed)
        scen_id = f"scen_ring_{seed}"
        scen = db.query(ScenarioDefinition).filter_by(id=scen_id).first()
        if scen:
            return scen

        scen = ScenarioDefinition(
            id=scen_id,
            name="Circular Mule Ring Gamma",
            scenario_type="MULE_RING",
            description="Four accounts engaged in circular transactions passing 180,000 INR repeatedly across cycles to obfuscate audit trails.",
            seed=seed
        )
        db.add(scen)
        db.commit()

        base_time = datetime(2026, 10, 26, 11, 0, 0, tzinfo=timezone.utc)
        ring_accs = [
            db.query(Account).filter_by(id=f"acc_mule_{20+i:03d}").first()
            for i in range(4)
        ]
        for a in ring_accs:
            a.is_mule = True
            a.mule_role = "LAYER"

        cycle_count = 2
        step = 0
        for cycle in range(cycle_count):
            for i in range(4):
                src = ring_accs[i]
                dst = ring_accs[(i + 1) % 4]
                tx_time = base_time + timedelta(minutes=40 * step)
                amt = 180000.0 - (step * 250.0)  # slight decay
                tx = Transaction(
                    id=f"tx_ring_{seed}_{step+1}",
                    tx_hash=hashlib.sha256(f"tx_ring_{seed}_{step+1}".encode()).hexdigest(),
                    scenario_id=scen.id,
                    source_account_id=src.id,
                    dest_account_id=dst.id,
                    amount=amt,
                    currency="INR",
                    timestamp=tx_time,
                    status="SETTLED",
                    channel="IMPS",
                    description=f"Circular Ring Cycle {cycle+1} Hop {i+1}",
                    has_token_lineage=False
                )
                db.add(tx)
                step += 1

        alert = Alert(
            id=f"alt_ring_{seed}",
            account_id=ring_accs[0].id,
            transaction_id=None,
            severity="HIGH",
            alert_type="MULE_RING",
            title="Circular Transaction Ring Detected",
            description=f"High modularity circular flow detected among accounts {ring_accs[0].account_number}, {ring_accs[1].account_number}, {ring_accs[2].account_number}.",
            status="OPEN"
        )
        db.add(alert)
        db.commit()
        return scen

    @classmethod
    def inject_layering_chain_scenario(cls, db: Session, seed: int = 104) -> ScenarioDefinition:
        """
        Scenario 4: Multi-Hop Layering Chain
        Funds traverse 5 hops across 5 different banking institutions in quick succession.
        """
        random.seed(seed)
        scen_id = f"scen_layer_{seed}"
        scen = db.query(ScenarioDefinition).filter_by(id=scen_id).first()
        if scen:
            return scen

        scen = ScenarioDefinition(
            id=scen_id,
            name="Deep Multi-Hop Layering Conduit Delta",
            scenario_type="LAYERING_CHAIN",
            description="Linear 5-hop fund layering across multiple banking institutions terminating at an unhosted crypto off-ramp bridge.",
            seed=seed
        )
        db.add(scen)
        db.commit()

        base_time = datetime(2026, 10, 25, 16, 0, 0, tzinfo=timezone.utc)
        chain_accs = [
            db.query(Account).filter_by(id=f"acc_mule_{30+i:03d}").first()
            for i in range(5)
        ]
        offramp = db.query(Account).filter_by(id="acc_offramp_003").first()
        
        all_chain = chain_accs + [offramp]
        amt = 320000.0

        for idx in range(len(all_chain) - 1):
            src = all_chain[idx]
            dst = all_chain[idx + 1]
            src.is_mule = True
            src.mule_role = "LAYER" if idx > 0 else "ORIGIN"
            
            tx_time = base_time + timedelta(hours=1.5 * idx)
            tx = Transaction(
                id=f"tx_layer_{seed}_{idx+1}",
                tx_hash=hashlib.sha256(f"tx_layer_{seed}_{idx+1}".encode()).hexdigest(),
                scenario_id=scen.id,
                source_account_id=src.id,
                dest_account_id=dst.id,
                amount=amt,
                currency="INR",
                timestamp=tx_time,
                status="SETTLED",
                channel="NEFT",
                description=f"Layering Hop {idx+1} Conduit",
                has_token_lineage=False
            )
            db.add(tx)
            amt -= 4000.0  # intermediate commission drop

        alert = Alert(
            id=f"alt_layer_{seed}",
            account_id=chain_accs[2].id,
            transaction_id=None,
            severity="MEDIUM",
            alert_type="LAYERING_CONDUIT",
            title="Multi-Hop Layering Bridge Identified",
            description=f"Account {chain_accs[2].account_number} acting as intermediate conduit in a 5-hop linear laundering sequence.",
            status="OPEN"
        )
        db.add(alert)
        db.commit()
        return scen

    @classmethod
    def inject_cross_bank_split_merge_scenario(cls, db: Session, seed: int = 105) -> ScenarioDefinition:
        """
        Scenario 5: Cross-Bank Split-and-Merge
        Origin account splits 600k INR across 3 intermediate mules in different banks,
        which simultaneously transfer to a final consolidator within 1 hour.
        """
        random.seed(seed)
        scen_id = f"scen_split_merge_{seed}"
        scen = db.query(ScenarioDefinition).filter_by(id=scen_id).first()
        if scen:
            return scen

        scen = ScenarioDefinition(
            id=scen_id,
            name="Cross-Bank Split-and-Merge Epsilon",
            scenario_type="CROSS_BANK_SPLIT_MERGE",
            description="Origin account splits 600,000 INR across 3 banks, which re-converge into a single receiver node.",
            seed=seed
        )
        db.add(scen)
        db.commit()

        base_time = datetime(2026, 10, 24, 10, 0, 0, tzinfo=timezone.utc)
        origin = db.query(Account).filter_by(id="acc_mule_040").first()
        collector = db.query(Account).filter_by(id="acc_mule_044").first()
        intermediaries = [
            db.query(Account).filter_by(id="acc_mule_041").first(),
            db.query(Account).filter_by(id="acc_mule_042").first(),
            db.query(Account).filter_by(id="acc_mule_043").first()
        ]
        
        origin.is_mule = True
        origin.mule_role = "ORIGIN"
        collector.is_mule = True
        collector.mule_role = "CASHOUT"

        # Step 1: Split
        for idx, inter in enumerate(intermediaries):
            inter.is_mule = True
            inter.mule_role = "BRIDGE"
            t1 = base_time + timedelta(minutes=15 * idx)
            tx_split = Transaction(
                id=f"tx_sm_{seed}_split_{idx+1}",
                tx_hash=hashlib.sha256(f"tx_sm_{seed}_split_{idx+1}".encode()).hexdigest(),
                scenario_id=scen.id,
                source_account_id=origin.id,
                dest_account_id=inter.id,
                amount=200000.0,
                currency="INR",
                timestamp=t1,
                status="SETTLED",
                channel="RTGS",
                description=f"Split Hop to Bank {inter.institution_id}",
                has_token_lineage=False
            )
            db.add(tx_split)

            # Step 2: Merge
            t2 = t1 + timedelta(minutes=30)
            tx_merge = Transaction(
                id=f"tx_sm_{seed}_merge_{idx+1}",
                tx_hash=hashlib.sha256(f"tx_sm_{seed}_merge_{idx+1}".encode()).hexdigest(),
                scenario_id=scen.id,
                source_account_id=inter.id,
                dest_account_id=collector.id,
                amount=198000.0,
                currency="INR",
                timestamp=t2,
                status="SETTLED",
                channel="IMPS",
                description=f"Merge Convergence to Collector",
                has_token_lineage=False
            )
            db.add(tx_merge)

        alert = Alert(
            id=f"alt_sm_{seed}",
            account_id=collector.id,
            transaction_id=None,
            severity="CRITICAL",
            alert_type="CROSS_BANK_SPLIT_MERGE",
            title="Cross-Bank Re-Convergence Detected",
            description=f"Collector {collector.account_number} merged 594,000 INR from 3 distinct financial institutions dispatched simultaneously.",
            status="OPEN"
        )
        db.add(alert)
        db.commit()
        return scen

    @classmethod
    def generate_custom_scenario(
        cls,
        db: Session,
        scenario_type: str,
        seed: int = 200,
        name_prefix: Optional[str] = None
    ) -> ScenarioDefinition:
        """
        Dynamically generates and injects a specified synthetic scenario on-demand.
        """
        if scenario_type == "RAPID_PASSTHROUGH":
            return cls.inject_rapid_passthrough_scenario(db, seed=seed)
        elif scenario_type == "SMURFING_FANIN":
            return cls.inject_smurfing_scenario(db, seed=seed)
        elif scenario_type == "MULE_RING":
            return cls.inject_mule_ring_scenario(db, seed=seed)
        elif scenario_type == "LAYERING_CHAIN":
            return cls.inject_layering_chain_scenario(db, seed=seed)
        elif scenario_type == "CROSS_BANK_SPLIT_MERGE":
            return cls.inject_cross_bank_split_merge_scenario(db, seed=seed)
        else:
            return cls.inject_rapid_passthrough_scenario(db, seed=seed)

