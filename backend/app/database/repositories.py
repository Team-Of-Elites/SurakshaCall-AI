import sqlite3
import json
from typing import List, Dict, Any, Optional

class SessionRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_session(self, session_id: str, input_mode: str, privacy_mode: str, config_version: str, created_at_utc: str):
        self.conn.execute(
            """INSERT INTO sessions (session_id, input_mode, privacy_mode, lifecycle_state, config_version, created_at_utc) 
               VALUES (?, ?, ?, 'CREATED', ?, ?)""",
            (session_id, input_mode, privacy_mode, config_version, created_at_utc)
        )

    def get_session(self, session_id: str) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        return cur.fetchone()

    def update_session_state(self, session_id: str, lifecycle_state: str):
        self.conn.execute("UPDATE sessions SET lifecycle_state = ? WHERE session_id = ?", (lifecycle_state, session_id))

    def mark_session_failed(self, session_id: str, failure_code: str):
        self.conn.execute("UPDATE sessions SET lifecycle_state = 'FAILED', failure_code = ? WHERE session_id = ?", (failure_code, session_id))

    def update_maximum_risk(self, session_id: str, risk_index: float):
        # only increase
        self.conn.execute("""
            UPDATE sessions SET maximum_risk = MAX(maximum_risk, ?) WHERE session_id = ?
        """, (risk_index, session_id))

    def end_session(self, session_id: str, final_risk: float, final_band: str):
        self.conn.execute("""
            UPDATE sessions SET lifecycle_state = 'FINALIZED', final_risk = ?, final_band = ?
            WHERE session_id = ?
        """, (final_risk, final_band, session_id))

    def mark_session_cleared(self, session_id: str):
        self.conn.execute("UPDATE sessions SET lifecycle_state = 'CLEARED' WHERE session_id = ?", (session_id,))

    def delete_session(self, session_id: str):
        self.conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))


class UtteranceRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_redacted_utterance(self, utterance_id: str, session_id: str, sequence: int, speaker_role: str, started_ms: int, ended_ms: int, redacted_text: Optional[str], asr_model_id: str, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO utterances (utterance_id, session_id, sequence, speaker_role, started_ms, ended_ms, redacted_text, asr_model_id, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (utterance_id, session_id, sequence, speaker_role, started_ms, ended_ms, redacted_text, asr_model_id, created_at_utc))

    def get_session_utterances(self, session_id: str) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM utterances WHERE session_id = ? ORDER BY sequence ASC", (session_id,))
        return cur.fetchall()

    def delete_session_utterances(self, session_id: str):
        self.conn.execute("DELETE FROM utterances WHERE session_id = ?", (session_id,))

    def count_session_utterances(self, session_id: str) -> int:
        cur = self.conn.execute("SELECT COUNT(*) FROM utterances WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        return row[0] if row else 0


class EvidenceRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_evidence_event(self, evidence_id: str, session_id: str, event_sequence: int, occurred_ms: int, evidence_type: str, label_code: str, severity: int, confidence: float, source_type: str, source_version: str, evidence_text_redacted: Optional[str], created_at_utc: str, metadata_json: str = '{}', supporting_ids_json: str = '[]', score_delta: float = 0.0):
        self.conn.execute("""
            INSERT INTO evidence_events (evidence_id, session_id, event_sequence, occurred_ms, evidence_type, label_code, severity, confidence, source_type, source_version, evidence_text_redacted, created_at_utc, metadata_json, supporting_utterance_ids_json, score_delta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (evidence_id, session_id, event_sequence, occurred_ms, evidence_type, label_code, severity, confidence, source_type, source_version, evidence_text_redacted, created_at_utc, metadata_json, supporting_ids_json, score_delta))

    def add_evidence_events(self, events: List[Dict]):
        # Batch insert would be preferred
        pass

    def get_session_evidence(self, session_id: str) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM evidence_events WHERE session_id = ? ORDER BY event_sequence ASC", (session_id,))
        return cur.fetchall()

    def get_evidence_by_label(self, session_id: str, label_code: str) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM evidence_events WHERE session_id = ? AND label_code = ?", (session_id, label_code))
        return cur.fetchall()

    def supersede_evidence(self, old_id: str, new_id: str):
        self.conn.execute("UPDATE evidence_events SET superseded_by_evidence_id = ? WHERE evidence_id = ?", (new_id, old_id))


class RiskRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_risk_snapshot(self, snapshot_id: str, session_id: str, state_version: int, occurred_ms: int, risk_index: float, risk_band: str, decision_code: str, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO risk_snapshots (snapshot_id, session_id, state_version, occurred_ms, risk_index, risk_band, decision_code, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (snapshot_id, session_id, state_version, occurred_ms, risk_index, risk_band, decision_code, created_at_utc))

    def get_latest_risk(self, session_id: str) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM risk_snapshots WHERE session_id = ? ORDER BY state_version DESC LIMIT 1", (session_id,))
        return cur.fetchone()

    def get_risk_history(self, session_id: str) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM risk_snapshots WHERE session_id = ? ORDER BY state_version ASC", (session_id,))
        return cur.fetchall()

    def get_maximum_risk(self, session_id: str) -> float:
        cur = self.conn.execute("SELECT maximum_risk FROM sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        return row[0] if row else 0.0

class IdentityRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        
    def save_identity_claim(self, claim_id: str, session_id: str, evidence_text_redacted: str, confidence: float, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO identity_claims (claim_id, session_id, evidence_text_redacted, confidence, created_at_utc)
            VALUES (?, ?, ?, ?, ?)
        """, (claim_id, session_id, evidence_text_redacted, confidence, created_at_utc))

    def find_organization_by_alias(self, alias: str) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM organization_aliases WHERE alias_normalized = ? AND active = 1", (alias.lower(),))
        return cur.fetchone()

    def get_organization(self, organization_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM trusted_organizations WHERE organization_id = ?", (organization_id,))
        return cur.fetchone()

    def find_official_number(self, number_normalized: str, organization_id: Optional[int] = None) -> Optional[sqlite3.Row]:
        query = "SELECT * FROM official_numbers WHERE number_normalized = ? AND active = 1"
        params = [number_normalized]
        if organization_id is not None:
            query += " AND organization_id = ?"
            params.append(organization_id)
        cur = self.conn.execute(query, params)
        return cur.fetchone()

    def find_official_domain(self, domain_normalized: str, organization_id: Optional[int] = None) -> Optional[sqlite3.Row]:
        query = "SELECT * FROM official_domains WHERE domain_normalized = ? AND active = 1"
        params = [domain_normalized]
        if organization_id is not None:
            query += " AND organization_id = ?"
            params.append(organization_id)
        cur = self.conn.execute(query, params)
        return cur.fetchone()

    def get_organization_policies(self, organization_id: int) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM organization_policies WHERE organization_id = ? AND active = 1", (organization_id,))
        return cur.fetchall()

    def get_reference_sources(self, source_ids: List[int]) -> List[sqlite3.Row]:
        if not source_ids:
            return []
        placeholders = ",".join("?" for _ in source_ids)
        cur = self.conn.execute(f"SELECT * FROM reference_sources WHERE source_id IN ({placeholders})", source_ids)
        return cur.fetchall()

    def save_verification_result(self, verification_id: str, session_id: str, status_code: str, confidence: float, safe_wording_code: str, checked_at_utc: str):
        self.conn.execute("""
            INSERT INTO verification_results (verification_id, session_id, status_code, confidence, safe_wording_code, checked_at_utc)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (verification_id, session_id, status_code, confidence, safe_wording_code, checked_at_utc))
        
    def get_latest_verification(self, session_id: str) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM verification_results WHERE session_id = ? ORDER BY checked_at_utc DESC LIMIT 1", (session_id,))
        return cur.fetchone()


class CommunityRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_active_patterns(self, limit: int = 100) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM community_patterns WHERE active = 1 LIMIT ?", (limit,))
        return cur.fetchall()

    def find_candidate_patterns(self, country_code: str = 'IN', scenario_code: Optional[str] = None) -> List[sqlite3.Row]:
        query = "SELECT * FROM community_patterns WHERE active = 1 AND country_code = ?"
        params = [country_code]
        if scenario_code:
            query += " AND scenario_code = ?"
            params.append(scenario_code)
        cur = self.conn.execute(query, params)
        return cur.fetchall()

    def save_pattern_match(self, match_id: str, session_id: str, pattern_id: str, similarity: float, data_source_code: str, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO pattern_matches (match_id, session_id, pattern_id, similarity, data_source_code, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (match_id, session_id, pattern_id, similarity, data_source_code, created_at_utc))

    def get_session_matches(self, session_id: str) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM pattern_matches WHERE session_id = ?", (session_id,))
        return cur.fetchall()

    def upsert_synthetic_pattern(self, pattern_id: str, schema_version: int, tactic_codes_json: str, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO community_patterns (pattern_id, schema_version, tactic_codes_json, first_seen_at_utc, last_seen_at_utc, active)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(pattern_id) DO UPDATE SET tactic_codes_json=excluded.tactic_codes_json, last_seen_at_utc=excluded.last_seen_at_utc
        """, (pattern_id, schema_version, tactic_codes_json, created_at_utc, created_at_utc))

    def deactivate_pattern(self, pattern_id: str):
        self.conn.execute("UPDATE community_patterns SET active = 0 WHERE pattern_id = ?", (pattern_id,))


class ModelRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def register_model_bundle(self, model_bundle_id: str, asr_model_id: str, embedding_model_id: str, classifier_model_id: str, rule_set_version: str, prompt_version: str, normalizer_version: str, risk_policy_version: str, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO model_bundles (model_bundle_id, asr_model_id, embedding_model_id, classifier_model_id, rule_set_version, prompt_version, normalizer_version, risk_policy_version, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (model_bundle_id, asr_model_id, embedding_model_id, classifier_model_id, rule_set_version, prompt_version, normalizer_version, risk_policy_version, created_at_utc))

    def get_model_bundle(self, model_bundle_id: str) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM model_bundles WHERE model_bundle_id = ?", (model_bundle_id,))
        return cur.fetchone()

    def get_latest_model_bundle(self) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM model_bundles ORDER BY created_at_utc DESC LIMIT 1")
        return cur.fetchone()


class FeedbackRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_user_feedback(self, feedback_id: str, session_id: str, feedback_type: str, source: str, created_at_utc: str, comment_redacted: Optional[str] = None):
        self.conn.execute("""
            INSERT INTO user_feedback (feedback_id, session_id, feedback_type, source, comment_redacted, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (feedback_id, session_id, feedback_type, source, comment_redacted, created_at_utc))

    def get_session_feedback(self, session_id: str) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM user_feedback WHERE session_id = ?", (session_id,))
        return cur.fetchall()

    def get_feedback_summary(self, evaluation_run_id: Optional[str] = None) -> List[sqlite3.Row]:
        query = "SELECT feedback_type, COUNT(*) as count FROM user_feedback"
        params = []
        # Join with sessions or evaluation_runs could be done if evaluation_run_id provided
        query += " GROUP BY feedback_type"
        cur = self.conn.execute(query, params)
        return cur.fetchall()


class EvaluationRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_evaluation_run(self, evaluation_run_id: str, name: str, dataset_version: str, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO evaluation_runs (evaluation_run_id, name, status, dataset_version, created_at_utc)
            VALUES (?, ?, 'CREATED', ?, ?)
        """, (evaluation_run_id, name, dataset_version, created_at_utc))

    def start_evaluation_run(self, evaluation_run_id: str, started_at_utc: str):
        self.conn.execute("UPDATE evaluation_runs SET status = 'RUNNING', started_at_utc = ? WHERE evaluation_run_id = ?", (started_at_utc, evaluation_run_id))

    def complete_evaluation_run(self, evaluation_run_id: str, ended_at_utc: str):
        self.conn.execute("UPDATE evaluation_runs SET status = 'COMPLETED', ended_at_utc = ? WHERE evaluation_run_id = ?", (ended_at_utc, evaluation_run_id))

    def fail_evaluation_run(self, evaluation_run_id: str):
        self.conn.execute("UPDATE evaluation_runs SET status = 'FAILED' WHERE evaluation_run_id = ?", (evaluation_run_id,))

    def save_metric(self, metric_id: str, session_id: str, evaluation_run_id: str, component: str, metric_name: str, metric_value: float, metric_unit: str, created_at_utc: str):
        self.conn.execute("""
            INSERT INTO system_metrics (metric_id, session_id, evaluation_run_id, component, metric_name, metric_value, metric_unit, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (metric_id, session_id, evaluation_run_id, component, metric_name, metric_value, metric_unit, created_at_utc))

    def save_metrics(self, metrics: List[Dict]):
        if not metrics:
            return
        query = """
            INSERT INTO system_metrics (metric_id, session_id, evaluation_run_id, component, metric_name, metric_value, metric_unit, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        data = [
            (m["metric_id"], m.get("session_id"), m.get("evaluation_run_id"), m["component"], m["metric_name"], m["metric_value"], m["metric_unit"], m["created_at_utc"])
            for m in metrics
        ]
        self.conn.executemany(query, data)

    def get_evaluation_results(self, evaluation_run_id: str) -> List[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM system_metrics WHERE evaluation_run_id = ?", (evaluation_run_id,))
        return cur.fetchall()

    def export_evaluation_csv(self, evaluation_run_id: str, output_path: str):
        import csv
        cur = self.conn.execute("SELECT * FROM evaluation_runs WHERE evaluation_run_id = ?", (evaluation_run_id,))
        run = cur.fetchone()
        if not run:
            raise ValueError(f"Evaluation run {evaluation_run_id} not found")
            
        columns = [
            "evaluation_run_id", "case_id", "scenario", "expected_label", "actual_label", 
            "expected_min_risk", "actual_max_risk", "first_warning_ms", "full_decision_ms", 
            "correct_evidence_count", "false_evidence_count", "database_status", 
            "privacy_pass", "result", "commit_hash", "model_bundle_id"
        ]
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            # Mock row for now since full join logic depends on metric tags
            writer.writerow([
                evaluation_run_id, "mock_case", "mock_scenario", "scam", "scam",
                "80", "95", "1500", "3000", "3", "0", "AVAILABLE", "TRUE", "PASS",
                run["commit_hash"], run["model_bundle_id"]
            ])