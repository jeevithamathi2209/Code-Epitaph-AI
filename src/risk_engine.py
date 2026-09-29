# ==========================================================
# CODE EPITAPH AI
# RISK INTELLIGENCE ENGINE
# ==========================================================


# ==========================================================
# BASIC SYSTEM RISK
# ==========================================================

def calculate_risk_score(analysis):
    """
    Calculate a basic dataset-level structural risk score.
    Score range: 0-100.
    """

    score = 0

    missing = analysis.get("missing_values", 0)

    if missing > 100:
        score += 25
    elif missing > 50:
        score += 15
    elif missing > 0:
        score += 5

    duplicates = analysis.get("duplicate_rows", 0)

    if duplicates > 100:
        score += 25
    elif duplicates > 20:
        score += 15
    elif duplicates > 0:
        score += 5

    columns = analysis.get("total_columns", 0)

    if columns > 30:
        score += 20
    elif columns > 15:
        score += 10
    elif columns > 5:
        score += 5

    return min(score, 100)


def classify_risk(score):
    """
    Convert risk score into a risk level.
    """

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def generate_risk_report(analysis):
    """
    Generate a basic risk report.
    """

    score = calculate_risk_score(analysis)

    return {
        "risk_score": score,
        "risk_level": classify_risk(score)
    }


# ==========================================================
# COMPONENT RISK INTELLIGENCE
# ==========================================================

def calculate_component_risk_score(
    base_risk,
    dependency_count,
    failure_impact,
    centrality,
    maintenance_status,
    max_dependencies=1,
    max_failure_impact=1
):
    """
    Calculate component-level structural risk.

    Factors:
    - Base dataset risk
    - Dependency complexity
    - Failure impact
    - Graph centrality
    - Maintenance condition

    Score range: 0-100.
    """

    base_risk = float(base_risk)
    dependency_count = float(dependency_count)
    failure_impact = float(failure_impact)
    centrality = float(centrality)

    max_dependencies = max(
        float(max_dependencies),
        1
    )

    max_failure_impact = max(
        float(max_failure_impact),
        1
    )

    # ------------------------------------------------------
    # NORMALIZED STRUCTURAL FACTORS
    # ------------------------------------------------------

    dependency_factor = min(
        dependency_count / max_dependencies,
        1
    )

    failure_factor = min(
        failure_impact / max_failure_impact,
        1
    )

    centrality_factor = min(
        centrality,
        1
    )

    # ------------------------------------------------------
    # MAINTENANCE FACTOR
    # ------------------------------------------------------

    status = str(
        maintenance_status
    ).lower()

    if status == "legacy":
        maintenance_factor = 1.0

    elif status == "maintenance":
        maintenance_factor = 0.65

    else:
        maintenance_factor = 0.20

    # ------------------------------------------------------
    # WEIGHTED STRUCTURAL RISK MODEL
    # ------------------------------------------------------

    risk = (
        base_risk * 0.10
        + dependency_factor * 25
        + failure_factor * 30
        + centrality_factor * 20
        + maintenance_factor * 15
    )

    return round(
        min(max(risk, 0), 100),
        1
    )


# ==========================================================
# COMPONENT PRIORITY ENGINE
# ==========================================================

def calculate_priority_score(
    risk_score,
    dependency_count,
    maintenance_status
):
    """
    Calculate component priority.

    Combines:
    - Structural risk
    - Dependency complexity
    - Maintenance condition

    Score range: 0-100.
    """

    risk_score = float(risk_score)

    dependency_count = float(
        dependency_count
    )

    status = str(
        maintenance_status
    ).lower()

    # Risk contribution: 60%
    risk_component = (
        risk_score * 0.60
    )

    # Dependency contribution: 25%
    dependency_component = min(
        dependency_count * 5,
        25
    )

    # Maintenance contribution: 15%
    if status == "legacy":
        maintenance_component = 15

    elif status == "maintenance":
        maintenance_component = 10

    else:
        maintenance_component = 3

    priority = (
        risk_component
        + dependency_component
        + maintenance_component
    )

    return round(
        min(priority, 100),
        1
    )


def classify_priority(priority_score):
    """
    Convert priority score into an action level.
    """

    if priority_score >= 75:
        return "CRITICAL"

    elif priority_score >= 55:
        return "HIGH"

    elif priority_score >= 35:
        return "MEDIUM"

    return "LOW"


def generate_priority_report(
    risk_score,
    dependency_count,
    maintenance_status
):
    """
    Generate complete priority assessment.
    """

    priority_score = calculate_priority_score(
        risk_score,
        dependency_count,
        maintenance_status
    )

    priority_level = classify_priority(
        priority_score
    )

    return {
        "priority_score": priority_score,
        "priority_level": priority_level
    }


# ==========================================================
# SYSTEM HEALTH ENGINE
# ==========================================================

def calculate_system_health(
    average_risk,
    critical_components,
    high_priority_components,
    dependency_density
):
    """
    Calculate overall system health.

    Score range: 0-100.
    Higher score = healthier system.
    """

    average_risk = float(
        average_risk
    )

    critical_components = int(
        critical_components
    )

    high_priority_components = int(
        high_priority_components
    )

    dependency_density = float(
        dependency_density
    )

    health_score = 100

    # Risk penalty
    health_score -= (
        average_risk * 0.45
    )

    # Critical component penalty
    health_score -= (
        critical_components * 8
    )

    # High priority penalty
    health_score -= (
        high_priority_components * 4
    )

    # Dependency complexity penalty
    health_score -= (
        dependency_density * 10
    )

    return round(
        max(
            0,
            min(
                100,
                health_score
            )
        ),
        1
    )


def classify_system_health(
    health_score
):
    """
    Convert health score into system condition.
    """

    if health_score >= 75:
        return "HEALTHY"

    elif health_score >= 55:
        return "WATCH"

    elif health_score >= 35:
        return "AT RISK"

    return "CRITICAL"


def generate_system_health_report(
    average_risk,
    critical_components,
    high_priority_components,
    dependency_density
):
    """
    Generate complete system health report.
    """

    health_score = calculate_system_health(
        average_risk,
        critical_components,
        high_priority_components,
        dependency_density
    )

    health_status = classify_system_health(
        health_score
    )

    return {
        "health_score": health_score,
        "health_status": health_status
    }


# ==========================================================
# EXPLAINABLE RISK ENGINE
# ==========================================================

def generate_component_explanation(
    risk_score,
    dependency_count,
    maintenance_status,
    priority_score,
    failure_impact
):
    """
    Generate an explainable component assessment.
    """

    reasons = []
    recommendations = []

    # ------------------------------------------------------
    # RISK FACTOR
    # ------------------------------------------------------

    if risk_score >= 70:

        reasons.append(
            "The component has a high structural risk score."
        )

        recommendations.append(
            "Perform a detailed technical review."
        )

    elif risk_score >= 40:

        reasons.append(
            "The component has a moderate structural risk score."
        )

        recommendations.append(
            "Monitor the component during maintenance cycles."
        )

    else:

        reasons.append(
            "The component currently has a relatively low structural risk score."
        )

    # ------------------------------------------------------
    # DEPENDENCY FACTOR
    # ------------------------------------------------------

    if dependency_count >= 4:

        reasons.append(
            f"It has a high dependency count ({dependency_count}), "
            "increasing structural complexity."
        )

        recommendations.append(
            "Review dependency relationships and reduce unnecessary coupling."
        )

    elif dependency_count >= 2:

        reasons.append(
            f"It has {dependency_count} dependencies, "
            "creating moderate structural complexity."
        )

    else:

        reasons.append(
            "It has relatively few direct dependencies."
        )

    # ------------------------------------------------------
    # MAINTENANCE FACTOR
    # ------------------------------------------------------

    status = str(
        maintenance_status
    ).lower()

    if status == "legacy":

        reasons.append(
            "The component is marked as legacy."
        )

        recommendations.append(
            "Consider modernization or controlled migration."
        )

    elif status == "maintenance":

        reasons.append(
            "The component is currently under maintenance."
        )

        recommendations.append(
            "Track maintenance changes and regression risk."
        )

    else:

        reasons.append(
            "The component is currently marked as active."
        )

    # ------------------------------------------------------
    # PRIORITY FACTOR
    # ------------------------------------------------------

    if priority_score >= 75:

        reasons.append(
            f"Its priority score is {priority_score}/100, "
            "placing it in the critical range."
        )

        recommendations.append(
            "Give this component high attention during planning."
        )

    elif priority_score >= 55:

        reasons.append(
            f"Its priority score is {priority_score}/100, "
            "placing it in the high-priority range."
        )

        recommendations.append(
            "Include this component in the near-term modernization plan."
        )

    elif priority_score >= 35:

        reasons.append(
            f"Its priority score is {priority_score}/100, "
            "placing it in the medium-priority range."
        )

    # ------------------------------------------------------
    # FAILURE IMPACT
    # ------------------------------------------------------

    if failure_impact >= 3:

        reasons.append(
            f"A failure could affect approximately "
            f"{failure_impact} downstream components."
        )

        recommendations.append(
            "Evaluate recovery and dependency isolation strategies."
        )

    elif failure_impact > 0:

        reasons.append(
            f"A failure may affect "
            f"{failure_impact} downstream component(s)."
        )

        recommendations.append(
            "Review downstream dependency relationships."
        )

    else:

        reasons.append(
            "No downstream impact was identified in the current graph."
        )

    # ------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------

    if priority_score >= 75:

        summary = (
            "This component requires immediate technical attention "
            "based on the combined structural risk indicators."
        )

    elif priority_score >= 55:

        summary = (
            "This component should receive closer monitoring "
            "because multiple structural risk indicators are present."
        )

    elif priority_score >= 35:

        summary = (
            "This component has moderate structural concerns "
            "and should be monitored during future maintenance."
        )

    else:

        summary = (
            "This component currently shows relatively low "
            "structural risk in the analyzed dataset."
        )

    return {
        "summary": summary,
        "reasons": reasons,
        "recommendations": recommendations
    }