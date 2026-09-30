import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

from src.data_loader import load_data
from src.preprocessing import preprocess_data

from src.graph_engine import (
    create_dependency_graph,
    calculate_graph_metrics,
    find_high_dependency_components,
    find_impact_chain
)

from src.risk_engine import (
    calculate_risk_score,
    calculate_component_risk_score,
    classify_risk,
    calculate_priority_score,
    classify_priority,
    generate_system_health_report,
    generate_component_explanation
)

from src.anomaly_engine import (
    detect_anomalies,
    get_anomaly_summary
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Code Epitaph AI",
    
    layout="wide"
)


# ============================================================
# CUSTOM STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #30363d;
        background: #161b22;
    }

    .section-title {
        font-size: 26px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .info-box {
        padding: 18px;
        border-radius: 12px;
        background: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.title("Code Epitaph AI")

st.caption(
    "Legacy System Intelligence & Dependency Risk Analysis"
)


# ============================================================
# LOAD DATA
# ============================================================

DATA_PATH = "data/sample_data.csv"


try:
    df = load_data(DATA_PATH)
    df = preprocess_data(df)

except Exception as e:

    st.error(f"Unable to load dataset: {e}")
    st.stop()


# ============================================================
# CREATE DEPENDENCY GRAPH
# ============================================================

graph = create_dependency_graph(df)

graph_metrics = calculate_graph_metrics(graph)


# ============================================================
# COMPONENT METRICS
# ============================================================

failure_impact_map = {}

for component in graph.nodes():

    impact_chain = find_impact_chain(
        graph,
        component
    )

    failure_impact_map[component] = len(
        impact_chain
    )


df["failure_impact"] = (
    df["component"]
    .map(failure_impact_map)
    .fillna(0)
)


# ============================================================
# CENTRALITY
# ============================================================

centrality = nx.degree_centrality(graph)

df["centrality"] = (
    df["component"]
    .map(centrality)
    .fillna(0)
)


# ============================================================
# DEPENDENCY COUNT
# ============================================================

df["dependency_count"] = (
    df["dependency_list"]
    .fillna("")
    .apply(
        lambda x: len(
            [
                item
                for item in str(x).split(",")
                if item.strip()
            ]
        )
    )
)


# ============================================================
# BASE RISK
# ============================================================

df["risk_score"] = df.apply(
    lambda row: calculate_risk_score(
        row
    ),
    axis=1
)


df["risk_level"] = df[
    "risk_score"
].apply(
    classify_risk
)


# ============================================================
# COMPONENT RISK
# ============================================================

max_dependencies = max(
    df["dependency_count"].max(),
    1
)

max_failure_impact = max(
    df["failure_impact"].max(),
    1
)


df["component_risk"] = df.apply(
    lambda row: calculate_component_risk_score(
        base_risk=row["risk_score"],
        dependency_count=row["dependency_count"],
        failure_impact=row["failure_impact"],
        centrality=row["centrality"],
        maintenance_status=row["maintenance_status"],
        max_dependencies=max_dependencies,
        max_failure_impact=max_failure_impact
    ),
    axis=1
)


df["risk_score"] = df[
    "component_risk"
]


df["risk_level"] = df[
    "risk_score"
].apply(
    classify_risk
)


# ============================================================
# PRIORITY ENGINE
# ============================================================

df["priority_score"] = df.apply(
    lambda row: calculate_priority_score(
        risk_score=row["risk_score"],
        dependency_count=row["dependency_count"],
        maintenance_status=row["maintenance_status"]
    ),
    axis=1
)


df["priority_level"] = df[
    "priority_score"
].apply(
    classify_priority
)


# ============================================================
# AI ANOMALY DETECTION
# ============================================================

try:

    df = detect_anomalies(df)

    anomaly_summary = get_anomaly_summary(
        df
    )

except Exception as e:

    st.warning(
        f"AI anomaly detection unavailable: {e}"
    )

    df["anomaly_status"] = "UNAVAILABLE"
    df["anomaly_score"] = 0

    anomaly_summary = {
        "total_components": len(df),
        "anomalous_components": 0,
        "normal_components": len(df),
        "anomaly_rate": 0
    }


# ============================================================
# SYSTEM HEALTH
# ============================================================

average_risk = df[
    "risk_score"
].mean()


critical_components = int(
    (
        df["priority_level"]
        == "CRITICAL"
    ).sum()
)


high_priority_components = int(
    (
        df["priority_level"]
        == "HIGH"
    ).sum()
)


dependency_density = (
    graph_metrics["graph_density"]
)


system_health = generate_system_health_report(
    average_risk=average_risk,
    critical_components=critical_components,
    high_priority_components=high_priority_components,
    dependency_density=dependency_density
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Code Epitaph AI")

st.sidebar.caption(
    "Legacy System Intelligence"
)


page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Component Intelligence",
        "Risk Prioritization",
        "Dependency Analysis",
        "Failure Simulator",
        "Modernization Roadmap",
        "AI Anomaly Intelligence",
        "Dataset"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.header("System Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Components",
        graph_metrics["total_components"]
    )

    col2.metric(
        "Dependencies",
        graph_metrics["total_dependencies"]
    )

    col3.metric(
        "Legacy Components",
        int(
            (
                df["maintenance_status"]
                .str.lower()
                == "legacy"
            ).sum()
        )
    )

    col4.metric(
        "Average Risk",
        f"{average_risk:.1f}/100"
    )


    st.divider()

    # --------------------------------------------------------
    # SYSTEM HEALTH
    # --------------------------------------------------------

    st.subheader(
        "System Health Index"
    )

    health_score = float(
        system_health["health_score"]
    )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health_score,
            title={
                "text": "System Health"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "thickness": 0.35
                }
            }
        )
    )

    fig.update_layout(
        height=320
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    st.subheader(
        "Risk Distribution"
    )

    risk_counts = (
        df["risk_level"]
        .value_counts()
        .reset_index()
    )

    risk_counts.columns = [
        "Risk Level",
        "Components"
    ]

    fig = px.bar(
        risk_counts,
        x="Risk Level",
        y="Components",
        text="Components"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # MAINTENANCE STATUS
    # --------------------------------------------------------

    st.subheader(
        "Maintenance Status"
    )

    status_counts = (
        df["maintenance_status"]
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "Status",
        "Components"
    ]

    fig = px.pie(
        status_counts,
        names="Status",
        values="Components",
        hole=0.45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# COMPONENT INTELLIGENCE
# ============================================================

elif page == "Component Intelligence":

    st.header(
        "Component Intelligence"
    )

    selected_component = st.selectbox(
        "Select Component",
        df["component"].tolist()
    )


    row = df[
        df["component"]
        == selected_component
    ].iloc[0]


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Risk Score",
        f"{row['risk_score']:.1f}/100"
    )

    col2.metric(
        "Priority",
        row["priority_level"]
    )

    col3.metric(
        "Dependencies",
        int(row["dependency_count"])
    )

    col4.metric(
        "Failure Impact",
        int(row["failure_impact"])
    )


    st.divider()


    # --------------------------------------------------------
    # COMPONENT DETAILS
    # --------------------------------------------------------

    st.subheader(
        "Component Assessment"
    )

    explanation = generate_component_explanation(
        row["risk_score"],
        row["dependency_count"],
        row["maintenance_status"],
        row["priority_score"],
        row["failure_impact"]
    )

    st.info(
        explanation
    )


    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "Risk Factors"
        )

        st.progress(
            min(
                float(row["risk_score"]) / 100,
                1
            )
        )

        st.write(
            f"Risk Score: {row['risk_score']:.1f}"
        )


        st.progress(
            min(
                float(row["dependency_count"])
                / max_dependencies,
                1
            )
        )

        st.write(
            f"Dependency Complexity: "
            f"{int(row['dependency_count'])}"
        )


        st.progress(
            min(
                float(row["failure_impact"])
                / max_failure_impact,
                1
            )
        )

        st.write(
            f"Failure Impact: "
            f"{int(row['failure_impact'])}"
        )


    with col2:

        st.subheader(
            "Component Profile"
        )

        st.write(
            f"**Language:** "
            f"{row['language']}"
        )

        st.write(
            f"**Version:** "
            f"{row['version']}"
        )

        st.write(
            f"**Maintenance:** "
            f"{row['maintenance_status']}"
        )

        st.write(
            f"**Centrality:** "
            f"{row['centrality']:.3f}"
        )

        st.write(
            f"**Priority Score:** "
            f"{row['priority_score']:.1f}"
        )


# ============================================================
# RISK PRIORITIZATION
# ============================================================

elif page == "Risk Prioritization":

    st.header(
        "Risk Prioritization Engine"
    )


    critical_count = int(
        (
            df["priority_level"]
            == "CRITICAL"
        ).sum()
    )

    high_count = int(
        (
            df["priority_level"]
            == "HIGH"
        ).sum()
    )

    average_priority = (
        df["priority_score"].mean()
    )


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Critical Priority",
        critical_count
    )

    col2.metric(
        "High Priority",
        high_count
    )

    col3.metric(
        "Average Priority",
        f"{average_priority:.1f}/100"
    )


    st.divider()


    # --------------------------------------------------------
    # PRIORITY CHART
    # --------------------------------------------------------

    priority_chart = (
        df[
            [
                "component",
                "priority_score"
            ]
        ]
        .sort_values(
            "priority_score",
            ascending=True
        )
    )


    fig = px.bar(
        priority_chart,
        x="priority_score",
        y="component",
        orientation="h",
        text="priority_score",
        title="Component Priority Scores"
    )

    fig.update_layout(
        xaxis_title="Priority Score",
        yaxis_title="Component"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RECOMMENDED ACTION ENGINE
    # --------------------------------------------------------

    def get_recommended_action(priority_level, maintenance_status):

        level = str(priority_level).upper()
        status = str(maintenance_status).lower()

        if level == "CRITICAL":
            return "Immediate modernization and dependency risk reduction."

        elif level == "HIGH":
            return "Prioritize refactoring and improve maintainability."

        elif level == "MEDIUM":
            return "Monitor closely and optimize dependency structure."

        if status == "legacy":
            return "Maintain with monitoring and plan future modernization."

        return "Continue regular maintenance and monitoring."


    action_df = df.copy()

    action_df["recommended_action"] = action_df.apply(
        lambda row: get_recommended_action(
            row["priority_level"],
            row["maintenance_status"]
        ),
        axis=1
    )


    st.subheader(
        "Recommended Engineering Actions"
    )

    action_display = action_df[
        [
            "component",
            "priority_level",
            "priority_score",
            "risk_score",
            "recommended_action"
        ]
    ].sort_values(
        "priority_score",
        ascending=False
    )

    st.dataframe(
        action_display,
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Risk Prioritization Table"
    )


    display_df = df[
        [
            "component",
            "risk_score",
            "priority_score",
            "priority_level",
            "dependency_count",
            "failure_impact",
            "maintenance_status"
        ]
    ].sort_values(
        "priority_score",
        ascending=False
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # DOWNLOAD RISK REPORT
    # --------------------------------------------------------

    report_df = display_df.copy()

    def report_recommended_action(level):

        if level == "CRITICAL":
            return "Immediate modernization and dependency reduction"

        elif level == "HIGH":
            return "Prioritize refactoring and improve maintainability"

        elif level == "MEDIUM":
            return "Monitor closely and optimize dependencies"

        return "Maintain and monitor"


    report_df["recommended_action"] = report_df[
        "priority_level"
    ].apply(report_recommended_action)

    report_df = report_df.rename(
        columns={
            "component": "Component",
            "risk_score": "Risk Score",
            "priority_score": "Priority Score",
            "priority_level": "Priority Level",
            "dependency_count": "Dependency Count",
            "failure_impact": "Failure Impact",
            "maintenance_status": "Maintenance Status",
            "recommended_action": "Recommended Action"
        }
    )

    report_csv = report_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Risk Report",
        data=report_csv,
        file_name="code_epitaph_risk_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# DEPENDENCY ANALYSIS
# ============================================================

elif page == "Dependency Analysis":

    st.header(
        "Dependency Analysis"
    )


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Components",
        graph_metrics["total_components"]
    )

    col2.metric(
        "Dependency Links",
        graph_metrics["total_dependencies"]
    )

    col3.metric(
        "Graph Density",
        graph_metrics["graph_density"]
    )


    st.divider()


    # --------------------------------------------------------
    # NETWORK GRAPH
    # --------------------------------------------------------

    st.subheader(
        "Dependency Network"
    )


    positions = nx.spring_layout(
        graph,
        seed=42
    )


    edge_x = []
    edge_y = []


    for source, target in graph.edges():

        x0, y0 = positions[source]
        x1, y1 = positions[target]

        edge_x.extend(
            [x0, x1, None]
        )

        edge_y.extend(
            [y0, y1, None]
        )


    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="none"
    )


    node_x = []
    node_y = []
    node_text = []


    for node in graph.nodes():

        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)

        node_text.append(
            str(node)
        )


    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hoverinfo="text",
        marker={
            "size": 20
        }
    )


    fig = go.Figure(
        data=[
            edge_trace,
            node_trace
        ]
    )


    fig.update_layout(
        height=650,
        showlegend=False,
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False
        },
        yaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False
        }
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # HIGH DEPENDENCY COMPONENTS
    # --------------------------------------------------------

    st.subheader(
        "High Dependency Components"
    )


    high_dependency = (
        find_high_dependency_components(
            graph
        )
    )


    dependency_df = pd.DataFrame(
        high_dependency,
        columns=[
            "Component",
            "Dependency Count"
        ]
    )


    st.dataframe(
        dependency_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FAILURE SIMULATOR
# ============================================================

elif page == "Failure Simulator":

    st.header(
        "What-If Failure Simulator"
    )

    st.caption(
        "Structural simulation of component failure impact"
    )

    st.info(
        "Select a component to simulate a failure and inspect "
        "downstream structural impact on the legacy system."
    )


    selected_component = st.selectbox(
        "Select component to fail",
        df["component"].tolist()
    )


    row = df[
        df["component"]
        == selected_component
    ].iloc[0]


    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "System Health",
        f"{system_health['health_score']:.1f}"
    )

    col2.metric(
        "Component Risk",
        f"{row['risk_score']:.1f}"
    )

    col3.metric(
        "Failure Impact",
        int(row["failure_impact"])
    )

    col4.metric(
        "Priority",
        row["priority_level"]
    )

    col5.metric(
        "Maintenance",
        row["maintenance_status"]
    )


    st.divider()

    # --------------------------------------------------------
    # FAILURE IMPACT SUMMARY
    # --------------------------------------------------------

    impact_col1, impact_col2 = st.columns(2)

    impact_col1.metric(
        "Dependency Count",
        int(row["dependency_count"])
    )

    impact_col2.metric(
        "Priority Score",
        f"{row["priority_score"]:.1f}/100"
    )


    dependencies = [
        item.strip()
        for item in str(
            row["dependency_list"]
        ).split(",")
        if item.strip()
    ]


    st.write(
        "**Direct Dependencies:**"
    )

    if dependencies:

        st.write(
            ", ".join(dependencies)
        )

    else:

        st.write(
            "No direct dependencies"
        )


    st.write(
        f"**Graph Centrality:** "
        f"{row['centrality']:.3f}"
    )


    if st.button(
        "⚠️ Simulate Component Failure",
        type="primary"
    ):

        affected_components = (
            find_impact_chain(
                graph,
                selected_component
            )
        )


        simulated_graph = graph.copy()

        if selected_component in simulated_graph:

            simulated_graph.remove_node(
                selected_component
            )


        simulated_metrics = (
            calculate_graph_metrics(
                simulated_graph
            )
        )


        affected_count = len(
            affected_components
        )


        failure_penalty = min(
            affected_count * 4,
            35
        )


        dependency_loss = (
            graph_metrics["total_dependencies"]
            - simulated_metrics[
                "total_dependencies"
            ]
        )


        density_change = (
            simulated_metrics[
                "graph_density"
            ]
            - graph_metrics[
                "graph_density"
            ]
        )


        simulated_health = max(
            0,
            min(
                100,
                system_health["health_score"]
                - failure_penalty
                - dependency_loss * 0.5
            )
        )


        health_delta = (
            simulated_health
            - system_health["health_score"]
        )


        st.divider()

        st.subheader(
            "Simulation Result"
        )


        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Current Health",
            f"{system_health['health_score']:.1f}"
        )

        col2.metric(
            "Simulated Health",
            f"{simulated_health:.1f}",
            delta=f"{health_delta:.1f}"
        )

        col3.metric(
            "Affected Components",
            affected_count
        )

        col4.metric(
            "Dependency Loss",
            dependency_loss
        )


        # ----------------------------------------------------
        # AFFECTED COMPONENTS
        # ----------------------------------------------------

        st.subheader(
            "Affected Component Chain"
        )


        if affected_components:

            affected_df = df[
                df["component"].isin(
                    affected_components
                )
            ][
                [
                    "component",
                    "risk_score",
                    "priority_level",
                    "maintenance_status"
                ]
            ]


            st.dataframe(
                affected_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No downstream components detected."
            )


        # ----------------------------------------------------
        # RECOVERY RECOMMENDATION
        # ----------------------------------------------------

        st.subheader(
            "Recovery Recommendation"
        )

        if row["priority_level"] == "CRITICAL":

            st.error(
                "Immediate isolation and modernization recommended. "
                "Review dependent components before restoring service."
            )

        elif row["priority_level"] == "HIGH":

            st.warning(
                "Prioritize recovery and dependency decoupling for this component."
            )

        elif row["priority_level"] == "MEDIUM":

            st.info(
                "Monitor the affected dependency chain and plan targeted remediation."
            )

        else:

            st.success(
                "Low-priority failure impact. Continue monitoring and document recovery steps."
            )


        # ----------------------------------------------------
        # STRUCTURAL CHANGE
        # ----------------------------------------------------

        st.subheader(
            "Structural Change"
        )


        change_df = pd.DataFrame(
            {
                "Metric": [
                    "Components",
                    "Dependencies",
                    "Graph Density"
                ],
                "Before": [
                    graph_metrics[
                        "total_components"
                    ],
                    graph_metrics[
                        "total_dependencies"
                    ],
                    graph_metrics[
                        "graph_density"
                    ]
                ],
                "After": [
                    simulated_metrics[
                        "total_components"
                    ],
                    simulated_metrics[
                        "total_dependencies"
                    ],
                    simulated_metrics[
                        "graph_density"
                    ]
                ]
            }
        )


        st.dataframe(
            change_df,
            use_container_width=True,
            hide_index=True
        )


        st.info(
            "This simulator performs a rule-based "
            "structural what-if analysis. It is intended "
            "for architecture risk exploration rather than "
            "production reliability prediction."
        )


# ============================================================
# MODERNIZATION ROADMAP
# ============================================================

elif page == "Modernization Roadmap":

    st.header(
        "Modernization Roadmap"
    )

    st.caption(
        "Prioritized engineering roadmap derived from structural risk"
    )


    roadmap_df = df.copy()


    # --------------------------------------------------------
    # MODERNIZATION SCORE
    # --------------------------------------------------------

    def calculate_modernization_score(row):

        risk_factor = (
            float(row["risk_score"])
            * 0.35
        )


        failure_factor = (
            min(
                float(row["failure_impact"])
                / max_failure_impact,
                1
            )
            * 25
        )


        priority_factor = (
            float(row["priority_score"])
            * 0.25
        )


        status = str(
            row["maintenance_status"]
        ).lower()


        if status == "legacy":

            status_factor = 15

        elif status == "maintenance":

            status_factor = 9

        else:

            status_factor = 3


        score = (
            risk_factor
            + failure_factor
            + priority_factor
            + status_factor
        )


        return round(
            min(
                max(score, 0),
                100
            ),
            1
        )


    roadmap_df[
        "modernization_score"
    ] = roadmap_df.apply(
        calculate_modernization_score,
        axis=1
    )


    # --------------------------------------------------------
    # MODERNIZATION CATEGORY
    # --------------------------------------------------------

    def modernization_category(score):

        if score >= 75:

            return "CRITICAL MODERNIZATION"

        elif score >= 55:

            return "REFACTOR"

        elif score >= 35:

            return "STABILIZE & MONITOR"

        return "MAINTAIN"


    roadmap_df[
        "modernization_category"
    ] = roadmap_df[
        "modernization_score"
    ].apply(
        modernization_category
    )


    # --------------------------------------------------------
    # EFFORT
    # --------------------------------------------------------

    def modernization_effort(row):

        score = float(
            row["modernization_score"]
        )

        dependencies = int(
            row["dependency_count"]
        )


        if score >= 75 or dependencies >= 4:

            return "HIGH"

        elif score >= 50 or dependencies >= 3:

            return "MEDIUM"

        return "LOW"


    roadmap_df[
        "effort"
    ] = roadmap_df.apply(
        modernization_effort,
        axis=1
    )


    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    def recommended_action(row):

        category = row[
            "modernization_category"
        ]


        if category == "CRITICAL MODERNIZATION":

            return (
                "Prioritize modernization, "
                "reduce dependency coupling, "
                "and prepare migration strategy."
            )


        elif category == "REFACTOR":

            return (
                "Refactor dependency structure "
                "and improve maintainability."
            )


        elif category == "STABILIZE & MONITOR":

            return (
                "Improve monitoring, documentation, "
                "and dependency stability."
            )


        return (
            "Continue maintenance and monitor "
            "structural risk."
        )


    roadmap_df[
        "recommended_action"
    ] = roadmap_df.apply(
        recommended_action,
        axis=1
    )


    # --------------------------------------------------------
    # ROADMAP ORDER
    # --------------------------------------------------------

    roadmap_df = roadmap_df.sort_values(
        [
            "modernization_score",
            "risk_score",
            "failure_impact"
        ],
        ascending=False
    ).reset_index(
        drop=True
    )


    roadmap_df[
        "roadmap_order"
    ] = range(
        1,
        len(roadmap_df) + 1
    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    critical_candidates = int(
        (
            roadmap_df[
                "modernization_score"
            ]
            >= 75
        ).sum()
    )


    modernization_candidates = int(
        (
            roadmap_df[
                "modernization_score"
            ]
            >= 55
        ).sum()
    )


    average_score = (
        roadmap_df[
            "modernization_score"
        ].mean()
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Total Components",
        len(roadmap_df)
    )

    col2.metric(
        "Modernization Candidates",
        modernization_candidates
    )

    col3.metric(
        "Critical Candidates",
        critical_candidates
    )

    col4.metric(
        "Average Score",
        f"{average_score:.1f}/100"
    )


    st.divider()


    # --------------------------------------------------------
    # MODERNIZATION CHART
    # --------------------------------------------------------

    fig = px.bar(
        roadmap_df.sort_values(
            "modernization_score"
        ),
        x="modernization_score",
        y="component",
        orientation="h",
        text="modernization_score",
        title="Modernization Priority"
    )


    fig.update_layout(
        xaxis_title="Modernization Score",
        yaxis_title="Component"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ROADMAP TABLE
    # --------------------------------------------------------

    st.subheader(
        "Engineering Roadmap"
    )


    roadmap_display = roadmap_df[
        [
            "roadmap_order",
            "component",
            "modernization_score",
            "modernization_category",
            "risk_score",
            "failure_impact",
            "effort"
        ]
    ]


    st.dataframe(
        roadmap_display,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # COMPONENT ASSESSMENT
    # --------------------------------------------------------

    st.subheader(
        "Modernization Assessment"
    )


    selected_component = st.selectbox(
        "Select component",
        roadmap_df[
            "component"
        ].tolist()
    )


    selected_row = roadmap_df[
        roadmap_df["component"]
        == selected_component
    ].iloc[0]


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Modernization Score",
        f"{selected_row['modernization_score']:.1f}"
    )

    col2.metric(
        "Risk Score",
        f"{selected_row['risk_score']:.1f}"
    )

    col3.metric(
        "Failure Impact",
        int(
            selected_row[
                "failure_impact"
            ]
        )
    )

    col4.metric(
        "Effort",
        selected_row["effort"]
    )


    st.info(
        selected_row[
            "recommended_action"
        ]
    )


    # --------------------------------------------------------
    # SCORE BREAKDOWN
    # --------------------------------------------------------

    st.subheader(
        "Score Breakdown"
    )


    breakdown = pd.DataFrame(
        {
            "Factor": [
                "Risk",
                "Failure Impact",
                "Priority",
                "Maintenance"
            ],
            "Contribution": [
                float(
                    selected_row[
                        "risk_score"
                    ]
                ) * 0.35,

                min(
                    float(
                        selected_row[
                            "failure_impact"
                        ]
                    )
                    / max_failure_impact,
                    1
                ) * 25,

                float(
                    selected_row[
                        "priority_score"
                    ]
                ) * 0.25,

                (
                    15
                    if str(
                        selected_row[
                            "maintenance_status"
                        ]
                    ).lower()
                    == "legacy"
                    else 9
                    if str(
                        selected_row[
                            "maintenance_status"
                        ]
                    ).lower()
                    == "maintenance"
                    else 3
                )
            ]
        }
    )


    fig = px.bar(
        breakdown,
        x="Factor",
        y="Contribution",
        text="Contribution",
        title="Modernization Score Factors"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # MODERNIZATION PHASES
    # --------------------------------------------------------

    st.subheader(
        "Modernization Phases"
    )


    phase1, phase2, phase3 = st.columns(3)


    with phase1:

        st.markdown(
            "### Phase 1 — Stabilize"
        )

        st.write(
            "Monitor critical components, "
            "document dependencies, and "
            "reduce immediate structural risk."
        )


    with phase2:

        st.markdown(
            "### Phase 2 — Refactor"
        )

        st.write(
            "Reduce unnecessary coupling, "
            "improve maintainability, and "
            "simplify dependency relationships."
        )


    with phase3:

        st.markdown(
            "### Phase 3 — Modernize"
        )

        st.write(
            "Replace high-risk legacy components "
            "and introduce a more maintainable "
            "architecture."
        )


# ============================================================
# AI ANOMALY INTELLIGENCE
# ============================================================

elif page == "AI Anomaly Intelligence":

    st.header(
        "🤖 AI Anomaly Intelligence"
    )

    st.caption(
        "Unsupervised detection of structurally unusual components"
    )


    # --------------------------------------------------------
    # AI SUMMARY
    # --------------------------------------------------------

    total_components = (
        anomaly_summary[
            "total_components"
        ]
    )

    anomalous_components = (
        anomaly_summary[
            "anomalous_components"
        ]
    )

    normal_components = (
        anomaly_summary[
            "normal_components"
        ]
    )

    anomaly_rate = (
        anomaly_summary[
            "anomaly_rate"
        ]
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Components Analyzed",
        total_components
    )

    col2.metric(
        "AI Anomalies",
        anomalous_components
    )

    col3.metric(
        "Normal Components",
        normal_components
    )

    col4.metric(
        "Anomaly Rate",
        f"{anomaly_rate:.1f}%"
    )


    st.divider()


    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    st.info(
        "The AI layer uses Isolation Forest, an "
        "unsupervised machine-learning algorithm, "
        "to identify components with unusual combinations "
        "of risk, dependency complexity, failure impact, "
        "centrality, and priority."
    )


    # --------------------------------------------------------
    # ANOMALY DISTRIBUTION
    # --------------------------------------------------------

    st.subheader(
        "AI Anomaly Distribution"
    )


    anomaly_counts = (
        df[
            "anomaly_status"
        ]
        .value_counts()
        .reset_index()
    )


    anomaly_counts.columns = [
        "Status",
        "Components"
    ]


    fig = px.pie(
        anomaly_counts,
        names="Status",
        values="Components",
        hole=0.45,
        title="Normal vs Anomalous Components"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ANOMALY SCORE
    # --------------------------------------------------------

    st.subheader(
        "Anomaly Score Analysis"
    )


    anomaly_chart = df[
        [
            "component",
            "anomaly_score",
            "anomaly_status"
        ]
    ].sort_values(
        "anomaly_score"
    )


    fig = px.bar(
        anomaly_chart,
        x="anomaly_score",
        y="component",
        color="anomaly_status",
        orientation="h",
        title="Isolation Forest Anomaly Scores"
    )


    fig.update_layout(
        xaxis_title="Anomaly Score",
        yaxis_title="Component"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ANOMALOUS COMPONENTS
    # --------------------------------------------------------

    st.subheader(
        "Detected Structural Anomalies"
    )


    anomalous_df = df[
        df["anomaly_status"]
        == "ANOMALOUS"
    ][
        [
            "component",
            "anomaly_score",
            "risk_score",
            "priority_score",
            "dependency_count",
            "failure_impact",
            "centrality",
            "maintenance_status"
        ]
    ].sort_values(
        "anomaly_score"
    )


    if anomalous_df.empty:

        st.success(
            "No structurally unusual components detected."
        )

    else:

        st.dataframe(
            anomalous_df,
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------------
    # COMPONENT INVESTIGATION
    # --------------------------------------------------------

    st.subheader(
        "AI Component Investigation"
    )


    selected_component = st.selectbox(
        "Select component",
        df["component"].tolist(),
        key="anomaly_component"
    )


    selected_row = df[
        df["component"]
        == selected_component
    ].iloc[0]


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "AI Status",
        selected_row[
            "anomaly_status"
        ]
    )

    col2.metric(
        "Anomaly Score",
        f"{selected_row['anomaly_score']:.4f}"
    )

    col3.metric(
        "Risk Score",
        f"{selected_row['risk_score']:.1f}"
    )

    col4.metric(
        "Priority",
        selected_row[
            "priority_level"
        ]
    )


    if selected_row[
        "anomaly_status"
    ] == "ANOMALOUS":

        st.warning(
            f"{selected_component} shows an unusual "
            "structural pattern compared with the "
            "other components in the analyzed system."
        )

    else:

        st.success(
            f"{selected_component} follows a "
            "relatively normal structural pattern "
            "within the analyzed system."
        )


    # --------------------------------------------------------
    # FEATURE PROFILE
    # --------------------------------------------------------

    feature_profile = pd.DataFrame(
        {
            "Feature": [
                "Risk Score",
                "Dependency Count",
                "Failure Impact",
                "Centrality",
                "Priority Score"
            ],
            "Value": [
                float(
                    selected_row[
                        "risk_score"
                    ]
                ),

                float(
                    selected_row[
                        "dependency_count"
                    ]
                ),

                float(
                    selected_row[
                        "failure_impact"
                    ]
                ),

                float(
                    selected_row[
                        "centrality"
                    ]
                ) * 100,

                float(
                    selected_row[
                        "priority_score"
                    ]
                )
            ]
        }
    )


    fig = px.bar(
        feature_profile,
        x="Feature",
        y="Value",
        text="Value",
        title="AI Feature Profile"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.caption(
        "Note: Anomaly detection identifies unusual "
        "patterns in the current dataset. An anomaly "
        "does not automatically mean a component is faulty."
    )


# ============================================================
# DATASET
# ============================================================

elif page == "Dataset":

    st.header(
        "Dataset Explorer"
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Rows",
        df.shape[0]
    )

    col2.metric(
        "Columns",
        df.shape[1]
    )

    col3.metric(
        "Missing Values",
        int(
            df.isnull()
            .sum()
            .sum()
        )
    )

    col4.metric(
        "Duplicate Rows",
        int(
            df.duplicated()
            .sum()
        )
    )


    st.divider()


    st.subheader(
        "Dataset Preview"
    )


    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Dataset Schema"
    )


    schema_df = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": [
                str(
                    df[column].dtype
                )
                for column in df.columns
            ],
            "Non-Null Values": [
                int(
                    df[column]
                    .notnull()
                    .sum()
                )
                for column in df.columns
            ]
        }
    )


    st.dataframe(
        schema_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SIDEBAR FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Code Epitaph AI • Structural + AI Intelligence"
)

st.sidebar.caption(
    "Python • Pandas • Scikit-learn • NetworkX • Plotly • Streamlit"
)