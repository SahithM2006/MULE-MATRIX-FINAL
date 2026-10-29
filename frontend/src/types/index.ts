export type PageTab = 
  | 'sentinel'
  | 'stream'
  | 'graph'
  | 'forensics'
  | 'detection'
  | 'observatory'
  | 'incident'
  | 'vault'
  | 'audit'
  | 'simulator'
  | 'replay'
  | 'settings'
  | 'health';

export interface SentinelSummary {
  total_accounts: number;
  total_transactions: number;
  total_institutions: number;
  active_alerts_count: number;
  critical_alerts_count: number;
  high_risk_accounts_count: number;
  total_volume_inr: number;
  recent_alerts: AlertItem[];
  active_scenarios: ScenarioInfo[];
}

export interface TransactionItem {
  id: string;
  tx_hash: string;
  scenario_id: string | null;
  source_account_id: string;
  source_account_number?: string;
  source_holder?: string;
  source_bank?: string;
  dest_account_id: string;
  dest_account_number?: string;
  dest_holder?: string;
  dest_bank?: string;
  amount: number;
  currency: string;
  timestamp: string;
  status: string;
  channel: string;
  description?: string;
  has_token_lineage: boolean;
  risk_flag?: string;
}

export interface AlertItem {
  id: string;
  account_id: string;
  account_number: string;
  holder_name: string;
  bank_name: string;
  transaction_id?: string;
  severity: 'INFO' | 'WARNING' | 'HIGH' | 'CRITICAL';
  alert_type: string;
  title: string;
  description: string;
  status: 'OPEN' | 'INVESTIGATING' | 'DISMISSED' | 'RESOLVED';
  created_at: string;
}

export interface AccountItem {
  id: string;
  account_number: string;
  holder_name: string;
  account_type: string;
  bank_name: string;
  balance: number;
  status: string;
  is_mule: boolean;
  mule_role: string;
}

export interface GraphNode {
  id: string;
  account_number: string;
  holder_name: string;
  bank_name: string;
  bank_swift: string;
  account_type: string;
  risk_score: number;
  risk_tier: string;
  is_start: boolean;
  is_offramp: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  amount: number;
  timestamp: string;
  channel: string;
  tx_hash: string;
  has_lineage: boolean;
}

export interface TraceResult {
  start_account_id: string;
  direction: string;
  max_hops: number;
  stop_reason: string;
  stop_reason_description: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  paths: string[][];
  total_volume_traced: number;
  nodes_count: number;
  edges_count: number;
}

export interface LineageEventItem {
  id: string;
  token_id: string;
  event_seq: number;
  tx_id: string;
  from_account_id: string;
  from_account_number?: string;
  to_account_id: string;
  to_account_number?: string;
  amount: number;
  previous_hash: string;
  current_hash: string;
  computed_hash?: string;
  is_valid: boolean;
  created_at: string;
  payload_json: string;
}

export interface LineageVerificationResult {
  token_id: string;
  is_intact: boolean;
  total_events: number;
  first_broken_seq: number | null;
  verification_status: 'VERIFIED_INTACT' | 'INTEGRITY_COMPROMISED' | 'NO_LINEAGE_FOUND';
  error_reason: string | null;
  chain: LineageEventItem[];
}

export interface EngineSignal {
  engine_id: string;
  engine_name: string;
  status: 'ACTIVE' | 'NOT_TRAINED' | 'UNAVAILABLE' | 'BENIGN' | 'SUSPICIOUS';
  score: number;
  weight: number;
  weighted_contribution: number;
  summary: string;
  details: Record<string, any>;
}

export interface AccountRiskProfile {
  account_id: string;
  account_number: string;
  holder_name: string;
  bank_name: string;
  bank_swift: string;
  account_type: string;
  balance: number;
  composite_risk_score: number;
  risk_tier: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  active_signals_count: number;
  narrative_explanation: string;
  signals: EngineSignal[];
  feature_metrics: Record<string, number>;
  rule_evidences: Array<{
    rule_code: string;
    rule_name: string;
    predicate_met: boolean;
    observed_value: number;
    threshold: number;
    time_window: string;
    bounded_contribution: number;
    description: string;
    evidence_refs: string[];
  }>;
}

export interface BenchmarkReport {
  evaluation_run_id: string;
  evaluated_at: string;
  test_seed: number;
  test_accounts_count: number;
  rule_baseline: {
    precision: number;
    recall: number;
    f1_score: number;
    false_positive_rate: number;
    confusion_matrix: { tp: number; fp: number; tn: number; fn: number };
  };
  candidate_detector: {
    precision: number;
    recall: number;
    f1_score: number;
    false_positive_rate: number;
    confusion_matrix: { tp: number; fp: number; tn: number; fn: number };
  };
  avg_latency_per_account_ms?: number;
  isolation_forest_status: string;
  graphsage_status: string;
  comparison_summary: string;
}

export interface CaseDetail {
  id: string;
  case_number: string;
  title: string;
  status: 'NEW' | 'IN_REVIEW' | 'ESCALATED' | 'FROZEN' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  primary_account_id: string;
  primary_account_number?: string;
  primary_holder_name?: string;
  primary_bank_name?: string;
  assigned_to: string;
  findings_summary: string;
  created_at: string;
  updated_at: string;
  notes: Array<{
    id: string;
    author: string;
    note_text: string;
    created_at: string;
  }>;
  status_events: Array<{
    id: string;
    old_status: string;
    new_status: string;
    changed_by: string;
    reason?: string;
    created_at: string;
  }>;
  artifacts: Array<{
    id: string;
    type: string;
    title: string;
    hash: string;
  }>;
}

export interface AuditEventItem {
  id: string;
  event_type: string;
  actor: string;
  target_type: string | null;
  target_id: string | null;
  action_details: string;
  previous_hash: string;
  current_hash: string;
  timestamp: string;
  success: boolean;
}

export interface AuditIntegrityReport {
  is_ledger_intact: boolean;
  total_events: number;
  first_tampered_index: number | null;
  verification_details: string;
  verified_at: string;
}

export interface ScenarioInfo {
  id: string;
  name: string;
  scenario_type: string;
  description: string;
  seed: number;
  created_at: string;
  transactions_count: number;
  accounts_count: number;
}

