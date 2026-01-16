# ----------------------------
# STEP 6: DERIVE FINAL EVALUATION FACTS (DETERMINISTIC)
# ----------------------------

def derive_evaluation_facts(evidence_output: dict) -> dict:
    """
    Deterministically derive final evaluation facts from evidence-only output.
    """

    test_outcome = evidence_output["test_outcome"]
    evidence = evidence_output["evidence"]
    scope = evidence_output["scope_assessment"]

    reason_codes = set(evidence.get("reason_codes", []))
    confidence_drivers = set(evidence.get("confidence_drivers", []))
    risk_codes = set(evidence.get("risk_codes", []))

    # ----------------------------
    # FIX ATTEMPT
    # ----------------------------

    is_fix_attempt = any(
        code in reason_codes
        for code in [
            "core_logic_modified",
            "addresses_boundary_condition",
            "addresses_state_cleanup",
            "addresses_control_flow_guard",
        ]
    )

    # ----------------------------
    # FIX COMPLETENESS
    # ----------------------------

    if is_fix_attempt and test_outcome["all_tests_passed"]:
        fix_completeness = "complete"
    elif is_fix_attempt and test_outcome["failed"] > 0:
        fix_completeness = "partial"
    elif not is_fix_attempt:
        fix_completeness = "none"
    else:
        fix_completeness = "unclear"

    # ----------------------------
    # ALIGNMENT CONFIDENCE (DETERMINISTIC BANDS)
    # ----------------------------

    if fix_completeness == "complete":
        alignment_confidence = 0.95
    elif fix_completeness == "partial":
        alignment_confidence = 0.6
    elif fix_completeness == "none":
        alignment_confidence = 0.2
    else:
        alignment_confidence = 0.4

    # ----------------------------
    # OVERALL CONFIDENCE
    # ----------------------------

    overall_confidence = alignment_confidence

    if (
        test_outcome["consistency"] == "high"
        and not test_outcome["flakiness_suspected"]
        and scope["scope_size"] == "small"
    ):
        overall_confidence = min(1.0, overall_confidence + 0.05)

    # ----------------------------
    # RISK ASSESSMENT
    # ----------------------------

    risks_present = len(risk_codes) > 0
    blocking_risk = any(
        risk in risk_codes
        for risk in [
            "algorithmic_rewrite",
            "state_mutation_risk",
        ]
    )

    # ----------------------------
    # SCOPE APPROPRIATENESS
    # ----------------------------

    scope_appropriate = scope["scope_size"] != "large"

    # ----------------------------
    # FINAL STRUCTURE
    # ----------------------------

    return {
        "schema_version": "1.0",

        "test_outcome": test_outcome,

        "diff_alignment": {
            "is_fix_attempt": is_fix_attempt,
            "addresses_dominant_failure_cluster": (
                test_outcome["dominant_failure_cluster_id"] is not None
            ),
            "addresses_multiple_failure_clusters": test_outcome["failure_cluster_count"] > 1,
            "alignment_confidence": alignment_confidence,
        },

        "fix_classification": {
            "fix_completeness": fix_completeness,
            "reason_codes": sorted(reason_codes),
        },

        "scope_assessment": {
            **scope,
            "scope_appropriate": scope_appropriate,
        },

        "risk_assessment": {
            "risks_present": risks_present,
            "blocking_risk": blocking_risk,
            "risk_codes": sorted(risk_codes),
        },

        "confidence_summary": {
            "overall_confidence": overall_confidence,
            "confidence_drivers": sorted(confidence_drivers),
        },
    }
