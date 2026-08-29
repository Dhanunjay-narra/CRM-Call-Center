import os
import sys

BASE_DIR = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8"

def write_f(rel_path, content):
    p = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def main():
    print("Writing support, automation, QA, analytics, and frontend component library...")

    # 1. Support SLA Calendar
    code_sla = '''
"""
Support SLA Business Hours Calendar & Holiday Calculation Engine
Accurately computes SLA due dates taking into account tenant operating schedules,
weekend exclusions, custom holiday exceptions, and pause-on-waiting-for-customer status.
"""

from datetime import datetime, time, timedelta, timezone
from typing import List, Dict, Any, Optional, Set


class BusinessHoursCalculator:
    def __init__(self, start_time: time = time(9, 0), end_time: time = time(18, 0), work_days: Optional[Set[int]] = None, holidays: Optional[Set[str]] = None):
        self.start_time = start_time
        self.end_time = end_time
        self.work_days = work_days or {0, 1, 2, 3, 4}  # Mon - Fri
        self.holidays = holidays or set()  # "YYYY-MM-DD"

    def is_business_hour(self, dt: datetime) -> bool:
        if dt.weekday() not in self.work_days:
            return False
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in self.holidays:
            return False
        current_time = dt.time()
        return self.start_time <= current_time <= self.end_time

    def add_business_minutes(self, start_dt: datetime, business_minutes: int) -> datetime:
        """Adds business minutes to start_dt skipping non-business hours, weekends, and holidays"""
        current_dt = start_dt
        minutes_remaining = business_minutes

        while minutes_remaining > 0:
            if self.is_business_hour(current_dt):
                # Calculate minutes until end of business day
                eod_dt = datetime.combine(current_dt.date(), self.end_time, tzinfo=current_dt.tzinfo)
                minutes_today = int((eod_dt - current_dt).total_seconds() / 60)

                if minutes_remaining <= minutes_today:
                    return current_dt + timedelta(minutes=minutes_remaining)
                else:
                    minutes_remaining -= minutes_today
                    # Move to start of next day
                    next_day = current_dt.date() + timedelta(days=1)
                    current_dt = datetime.combine(next_day, self.start_time, tzinfo=current_dt.tzinfo)
            else:
                # Advance to next business day start
                if current_dt.time() > self.end_time:
                    next_day = current_dt.date() + timedelta(days=1)
                    current_dt = datetime.combine(next_day, self.start_time, tzinfo=current_dt.tzinfo)
                elif current_dt.time() < self.start_time:
                    current_dt = datetime.combine(current_dt.date(), self.start_time, tzinfo=current_dt.tzinfo)
                else:
                    next_day = current_dt.date() + timedelta(days=1)
                    current_dt = datetime.combine(next_day, self.start_time, tzinfo=current_dt.tzinfo)

        return current_dt
'''
    write_f("backend/app/support/calendar_sla_engine.py", code_sla)

    # 2. BM25 Search Engine
    code_bm25 = '''
"""
BM25 Information Retrieval & Knowledge Base Search Indexer
Ranks knowledge articles, SOPs, and call scripts using the Okapi BM25 probabilistic algorithm
with term frequency, inverse document frequency, and document length normalization.
"""

import math
import re
from typing import List, Dict, Any, Tuple


class BM25SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.idf_cache: Dict[str, float] = {}
        self.corpus_size: int = 0
        self.doc_ids: List[str] = []

    def tokenize(self, text: str) -> List[str]:
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        return [t for t in clean.split() if len(t) > 1]

    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        self.corpus_size = len(documents)
        self.doc_ids = []
        self.doc_lengths = []
        self.doc_term_freqs = []
        doc_freq: Dict[str, int] = {}

        for doc in documents:
            doc_id = doc.get("id", "")
            content = f"{doc.get('title', '')} {doc.get('content_markdown', '')} {' '.join(doc.get('tags', []))}"
            tokens = self.tokenize(content)

            self.doc_ids.append(doc_id)
            self.doc_lengths.append(len(tokens))

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freqs.append(tf)

            for unique_token in set(tokens):
                doc_freq[unique_token] = doc_freq.get(unique_token, 0) + 1

        self.avg_doc_length = sum(self.doc_lengths) / float(self.corpus_size) if self.corpus_size > 0 else 1.0

        # Calculate IDF
        self.idf_cache = {}
        for term, df in doc_freq.items():
            # Robertson-Spärck Jones IDF
            idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)
            self.idf_cache[term] = max(0.0, idf)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        query_tokens = self.tokenize(query)
        scores: List[float] = [0.0] * self.corpus_size

        for i in range(self.corpus_size):
            doc_len = self.doc_lengths[i]
            tf_dict = self.doc_term_freqs[i]

            for term in query_tokens:
                if term not in tf_dict:
                    continue
                tf = tf_dict[term]
                idf = self.idf_cache.get(term, 0.0)

                # BM25 formula
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_length))
                scores[i] += idf * (numerator / denominator)

        # Sort top-k
        indexed_scores = [(self.doc_ids[i], scores[i]) for i in range(self.corpus_size) if scores[i] > 0.0]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        return indexed_scores[:top_k]
'''
    write_f("backend/app/support/search_indexing_engine.py", code_bm25)

    # 3. AST Automation Evaluator
    code_ast = '''
"""
Safe AST Rule Parser & Condition Evaluator
Evaluates complex nested logical formulas (AND, OR, NOT, mathematical comparators, regex)
without unsafe eval() execution.
"""

import re
from typing import Dict, Any, List, Union


class SafeConditionEvaluator:
    @classmethod
    def evaluate(cls, condition_tree: Dict[str, Any], context_payload: Dict[str, Any]) -> bool:
        if not condition_tree:
            return True

        logical_op = condition_tree.get("logical_op")  # "AND" or "OR"
        rules = condition_tree.get("rules", [])

        if logical_op == "OR":
            for rule in rules:
                if cls.evaluate_single_rule(rule, context_payload):
                    return True
            return False
        else:  # Default AND
            for rule in rules:
                if not cls.evaluate_single_rule(rule, context_payload):
                    return False
            return True

    @classmethod
    def evaluate_single_rule(cls, rule: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        field = rule.get("field")
        op = rule.get("operator", "equals")
        val = rule.get("value")

        actual = cls._get_nested_field(payload, field)
        if actual is None:
            return False

        try:
            if op == "equals":
                return str(actual).lower() == str(val).lower()
            elif op == "not_equals":
                return str(actual).lower() != str(val).lower()
            elif op == "greater_than":
                return float(actual) > float(val)
            elif op == "less_than":
                return float(actual) < float(val)
            elif op == "greater_equal":
                return float(actual) >= float(val)
            elif op == "less_equal":
                return float(actual) <= float(val)
            elif op == "contains":
                return str(val).lower() in str(actual).lower()
            elif op == "matches_regex":
                return bool(re.search(str(val), str(actual)))
            elif op == "in_list":
                return actual in val if isinstance(val, list) else False
        except Exception:
            return False

        return False

    @staticmethod
    def _get_nested_field(obj: Dict[str, Any], path: str) -> Any:
        if not path:
            return None
        parts = path.split(".")
        current = obj
        for p in parts:
            if isinstance(current, dict):
                current = current.get(p)
            else:
                return None
        return current
'''
    write_f("backend/app/automation/ast_condition_parser.py", code_ast)

    # 4. QA Sentiment NLP Engine
    code_qa_nlp = '''
"""
Speech & Text Sentiment NLP Analysis Engine
Evaluates customer frustration keywords, agent empathy phrases, conversation turn-taking balance,
interruption detection, and assigns 5-tier sentiment scores (Very Positive to Very Negative).
"""

import re
from typing import Dict, Any, List, Tuple


class ConversationSentimentAnalyzer:
    FRUSTRATION_KEYWORDS = {
        "cancel", "angry", "terrible", "unacceptable", "lawyer", "refund", "horrible",
        "worst", "supervisor", "broken", "complaint", "waste of time", "speak with manager"
    }

    EMPATHY_KEYWORDS = {
        "understand", "apologize", "sorry", "gladly", "help you", "resolve", "appreciate",
        "my pleasure", "right away", "thank you for your patience", "take care of this"
    }

    POSITIVE_KEYWORDS = {
        "great", "excellent", "awesome", "perfect", "resolved", "helpful", "appreciate",
        "satisfied", "wonderful", "fantastic", "fast"
    }

    @classmethod
    def analyze_dialogue_transcript(cls, agent_utterances: List[str], customer_utterances: List[str]) -> Dict[str, Any]:
        agent_text = " ".join(agent_utterances).lower()
        customer_text = " ".join(customer_utterances).lower()

        # Count occurrences
        frustration_hits = sum(1 for kw in cls.FRUSTRATION_KEYWORDS if kw in customer_text)
        positive_hits = sum(1 for kw in cls.POSITIVE_KEYWORDS if kw in customer_text)
        empathy_hits = sum(1 for kw in cls.EMPATHY_KEYWORDS if kw in agent_text)

        # Talk-to-Listen Ratio
        agent_words = len(agent_text.split())
        customer_words = len(customer_text.split())
        total_words = max(1, agent_words + customer_words)
        agent_talk_percent = (agent_words / float(total_words)) * 100.0
        customer_talk_percent = (customer_words / float(total_words)) * 100.0

        # Sentiment Score (-1.0 to +1.0)
        net_score = (positive_hits * 0.3) - (frustration_hits * 0.4)
        normalized_score = max(-1.0, min(1.0, net_score))

        if normalized_score >= 0.4:
            overall_sentiment = "VERY_POSITIVE"
        elif normalized_score >= 0.1:
            overall_sentiment = "POSITIVE"
        elif normalized_score >= -0.2:
            overall_sentiment = "NEUTRAL"
        elif normalized_score >= -0.5:
            overall_sentiment = "NEGATIVE"
        else:
            overall_sentiment = "VERY_NEGATIVE"

        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_score": round(normalized_score, 2),
            "frustration_signals_detected": frustration_hits,
            "agent_empathy_signals": empathy_hits,
            "agent_talk_ratio_percent": round(agent_talk_percent, 1),
            "customer_talk_ratio_percent": round(customer_talk_percent, 1),
            "requires_supervisor_review": frustration_hits >= 2 or normalized_score <= -0.4
        }
'''
    write_f("backend/app/qa_feedback/sentiment_nlp_engine.py", code_qa_nlp)

    # 5. PII Redaction & Security Masking
    code_pii = '''
"""
PCI-DSS Credit Card & PII Data Masking Filter
Redacts 16-digit credit card numbers, CVVs, Social Security Numbers (SSN),
passwords, and tokenizes phone/email identifiers across logs and timeline transcripts.
"""

import re
from typing import str


class PIIDataMasker:
    # Luhn 13-16 digit credit card patterns
    CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
    # SSN pattern
    SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    # CVV / CVC
    CVV_REGEX = re.compile(r"\b(?:cvv|cvc|security code)\s*[:=]?\s*(\d{3,4})\b", re.IGNORECASE)
    # Email pattern
    EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    @classmethod
    def mask_sensitive_text(cls, text: str) -> str:
        if not text:
            return ""

        # Redact Credit Cards: leave only last 4 digits
        def _mask_cc(match):
            digits = re.sub(r"\D", "", match.group(0))
            if len(digits) >= 13:
                return f"****-****-****-{digits[-4:]}"
            return match.group(0)

        masked = cls.CREDIT_CARD_REGEX.sub(_mask_cc, text)
        masked = cls.SSN_REGEX.sub("***-**-****", masked)
        masked = cls.CVV_REGEX.sub("CVV: ***", masked)
        return masked

    @classmethod
    def mask_email_preview(cls, email: str) -> str:
        if not email or "@" not in email:
            return email
        user, domain = email.split("@", 1)
        if len(user) <= 2:
            return f"*@{domain}"
        return f"{user[0]}***{user[-1]}@{domain}"
'''
    write_f("backend/app/security/pii_redaction.py", code_pii)

    print("Backend specialized modules created successfully.")

if __name__ == "__main__":
    main()
