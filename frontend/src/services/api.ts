import {
  SentinelSummary,
  TransactionItem,
  AlertItem,
  AccountItem,
  TraceResult,
  LineageVerificationResult,
  AccountRiskProfile,
  BenchmarkReport,
  CaseDetail,
  AuditEventItem,
  AuditIntegrityReport,
  ScenarioInfo
} from '../types';

const BASE_URL = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      },
      ...options
    });
    if (!res.ok) {
      if (res.status === 502 || res.status === 503 || res.status === 504) {
        throw new Error(
          `API Error [${res.status}]: Backend API service unreachable. Ensure FastAPI backend is running on http://127.0.0.1:8000.`
        );
      }
      const errorBody = await res.text();
      let parsedDetail = errorBody;
      try {
        const jsonErr = JSON.parse(errorBody);
        if (jsonErr && jsonErr.detail) parsedDetail = jsonErr.detail;
      } catch {
        // keep text
      }
      throw new Error(`API Error [${res.status}]: ${parsedDetail}`);
    }
    return res.json();
  } catch (err: any) {
    if (err.message && err.message.startsWith('API Error')) {
      throw err;
    }
    throw new Error(`Network Error: ${err.message || 'Failed to connect to backend API server.'}`);
  }
}

export const api = {
  // Observe
  getSentinelSummary: () => fetchJson<SentinelSummary>('/observe/sentinel'),
  getTransactions: (params?: {
    account_id?: string;
    min_amount?: number;
    max_amount?: number;
    channel?: string;
    status?: string;
    has_lineage?: boolean;
    scenario_id?: string;
    limit?: number;
    offset?: number;
  }) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') query.append(k, String(v));
      });
    }
    return fetchJson<TransactionItem[]>(`/observe/transactions?${query.toString()}`);
  },
  getAlerts: (params?: { severity?: string; status?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) query.append(k, String(v));
      });
    }
    return fetchJson<AlertItem[]>(`/observe/alerts?${query.toString()}`);
  },
  getAccounts: (params?: { query?: string; account_type?: string; is_mule?: boolean; limit?: number }) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) query.append(k, String(v));
      });
    }
    return fetchJson<AccountItem[]>(`/observe/accounts?${query.toString()}`);
  },

  // Trace
  runBfsTrace: (payload: {
    account_id: string;
    direction: string;
    max_hops?: number;
    lookback_hours?: number;
    lookahead_hours?: number;
    search_budget?: number;
  }) => fetchJson<TraceResult>('/trace/bfs', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getTokenLineage: (tokenId: string) => fetchJson<LineageVerificationResult>(`/trace/lineage/${tokenId}`),
  getAvailableTokens: () => fetchJson<Array<{
    token_id: string;
    total_events: number;
    origin_account_id: string;
    terminal_account_id: string;
    amount: number;
    created_at: string;
  }>>('/trace/tokens'),
  simulateTamperTest: (tokenId: string, tamperSeq: number = 1) => fetchJson<{
    tamper_simulation: string;
    simulated_tamper_seq: number;
    verification_result: LineageVerificationResult;
  }>(`/trace/lineage/tamper-test?token_id=${tokenId}&tamper_seq=${tamperSeq}`, {
    method: 'POST'
  }),

  // Detect
  getAccountRiskProfile: (accountId: string) => fetchJson<AccountRiskProfile>(`/detect/account/${accountId}`),
  getLatestBenchmark: () => fetchJson<BenchmarkReport>('/detect/benchmark'),
  runBenchmark: (seed: number = 105) => fetchJson<BenchmarkReport>(`/detect/benchmark/run?seed=${seed}`, {
    method: 'POST'
  }),

  // Respond
  getCases: (statusFilter?: string) => {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return fetchJson<CaseDetail[]>(`/respond/cases${query}`);
  },
  getCaseDetail: (caseId: string) => fetchJson<CaseDetail>(`/respond/cases/${caseId}`),
  createCase: (payload: {
    title: string;
    primary_account_id: string;
    priority?: string;
    assigned_to?: string;
    findings_summary?: string;
  }) => fetchJson<CaseDetail>('/respond/cases', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  addCaseNote: (caseId: string, payload: { author: string; note_text: string }) =>
    fetchJson<any>(`/respond/cases/${caseId}/notes`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  updateCaseStatus: (caseId: string, payload: { status: string; assigned_to?: string; status_change_reason?: string }) =>
    fetchJson<CaseDetail>(`/respond/cases/${caseId}/status`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    }),
  exportEvidenceDossier: (caseId: string) => fetchJson<{
    case_id: string;
    case_number: string;
    artifact_id: string;
    artifact_type: string;
    file_path: string;
    content_hash: string;
    dossier_summary: any;
    download_url: string;
  }>(`/respond/cases/${caseId}/export`, {
    method: 'POST'
  }),

  // Audit
  getAuditEvents: (limit: number = 50, offset: number = 0) =>
    fetchJson<AuditEventItem[]>(`/audit/events?limit=${limit}&offset=${offset}`),
  verifyAuditLedger: () => fetchJson<AuditIntegrityReport>('/audit/verify'),

  // Simulator
  getScenarios: () => fetchJson<ScenarioInfo[]>('/simulator/scenarios'),
  generateScenario: (payload: { scenario_type: string; seed?: number; accounts_count?: number; name_prefix?: string }) =>
    fetchJson<ScenarioInfo>('/simulator/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  // System
  getSystemHealth: () => fetchJson<any>('/system/health'),
  seedDataset: () => fetchJson<any>('/system/seed', { method: 'POST' })
};

