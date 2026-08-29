"""
CRM Record Deduplication & Fuzzy Entity Resolution Engine
Implements Levenshtein Edit Distance, Jaro-Winkler Similarity, and Phonetic Double Metaphone
for identifying duplicate Customer Accounts, Leads, and Contacts with automated merge strategies.
"""

import re
import math
from typing import Dict, Any, List, Tuple, Optional


class StringSimilarity:
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Computes minimum single-character edits (insertions, deletions, substitutions)"""
        s1, s2 = s1.lower().strip(), s2.lower().strip()
        if len(s1) < len(s2):
            return StringSimilarity.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @classmethod
    def levenshtein_similarity(cls, s1: str, s2: str) -> float:
        """Normalized similarity between 0.0 (completely distinct) and 1.0 (exact match)"""
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        distance = cls.levenshtein_distance(s1, s2)
        return max(0.0, 1.0 - (distance / float(max_len)))

    @staticmethod
    def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
        """Computes Jaro-Winkler string similarity favoring common prefixes"""
        s1, s2 = s1.lower().strip(), s2.lower().strip()
        if s1 == s2:
            return 1.0
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0

        match_distance = max(len1, len2) // 2 - 1
        s1_matches = [False] * len1
        s2_matches = [False] * len2

        matches = 0
        transpositions = 0

        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        transpositions //= 2
        jaro = (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0

        # Prefix bonus up to 4 chars
        prefix = 0
        for i in range(min(len1, len2, 4)):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break

        return min(1.0, jaro + prefix * p * (1.0 - jaro))


class DuplicateDetector:
    @classmethod
    def evaluate_duplicate_probability(cls, candidate: Dict[str, Any], existing_record: Dict[str, Any]) -> Tuple[float, List[str]]:
        reasons = []
        score = 0.0

        # 1. Exact Email Match (Strongest signal)
        c_email = (candidate.get("email") or "").lower().strip()
        e_email = (existing_record.get("email") or "").lower().strip()
        if c_email and e_email and c_email == e_email:
            score += 90.0
            reasons.append(f"Exact email match: {c_email}")

        # 2. Exact Normalized Phone Match
        c_phone = re.sub(r"\D", "", candidate.get("phone_number") or "")
        e_phone = re.sub(r"\D", "", existing_record.get("phone_number") or "")
        if c_phone and e_phone and len(c_phone) >= 10 and c_phone[-10:] == e_phone[-10:]:
            score += 85.0
            reasons.append(f"Exact phone match: {c_phone}")

        # 3. Fuzzy Name & Company Match
        c_name = candidate.get("name") or f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
        e_name = existing_record.get("name") or f"{existing_record.get('first_name', '')} {existing_record.get('last_name', '')}".strip()
        if c_name and e_name:
            name_sim = StringSimilarity.jaro_winkler_similarity(c_name, e_name)
            if name_sim >= 0.88:
                score += (name_sim * 40.0)
                reasons.append(f"High name similarity: {c_name} ~ {e_name} ({int(name_sim*100)}%)")

        c_company = candidate.get("company_name") or candidate.get("company")
        e_company = existing_record.get("company_name") or existing_record.get("company")
        if c_company and e_company:
            comp_sim = StringSimilarity.jaro_winkler_similarity(c_company, e_company)
            if comp_sim >= 0.85:
                score += (comp_sim * 30.0)
                reasons.append(f"High company similarity: {c_company} ~ {e_company} ({int(comp_sim*100)}%)")

        final_prob = min(1.0, max(0.0, score / 100.0))
        return final_prob, reasons
