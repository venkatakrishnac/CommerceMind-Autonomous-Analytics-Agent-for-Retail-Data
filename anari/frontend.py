import streamlit as st
import requests
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

API_URL = "http://localhost:8000/ask"

# --- Modern deep blue-to-teal gradient background ---
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(135deg, #232946 0%, #00c9a7 100%) !important;
        color: #e0e0e0;
        min-height: 100vh;
    }
    .grid-bg {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0;
        pointer-events: none;
        background-image: linear-gradient(to right, rgba(80,180,255,0.04) 1px, transparent 1px),
                          linear-gradient(to bottom, rgba(80,180,255,0.04) 1px, transparent 1px);
        background-size: 40px 40px;
    }
    </style>
    <div class='grid-bg'></div>
    """,
    unsafe_allow_html=True,
)

st.title("CommerceMind: Autonomous Analytics Agent for Retail Data")

st.write("Ask any question about your e-commerce data:")

question = st.text_input("Enter your question:")
show_chart = st.checkbox("Show chart if possible (bonus)", value=True)

# --- Helper: Infer intent from question ---
def infer_intent(q):
    q = q.lower()
    if any(word in q for word in ["trend", "over time", "growth", "change", "evolution", "history", "timeline"]):
        return "trend"
    if any(word in q for word in ["distribution", "histogram", "spread", "range", "boxplot"]):
        return "distribution"
    if any(word in q for word in ["proportion", "share", "percentage", "breakdown", "composition", "part of", "segment"]):
        return "proportion"
    if any(word in q for word in ["compare", "comparison", "top", "ranking", "most", "least", "highest", "lowest"]):
        return "comparison"
    if any(word in q for word in ["correlation", "relationship", "impact", "effect", "association"]):
        return "correlation"
    if any(word in q for word in ["map", "location", "region", "country", "state", "city"]):
        return "map"
    return None

if st.button("Run Query"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": question})
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        st.error(f"Error: {data['error']}")
                        if "sql" in data:
                            st.code(data["sql"], language="sql")
                    else:
                        st.success("Answer:")
                        df = None
                        if "results" in data and data["results"]:
                            df = pd.DataFrame(data["results"])
                            st.dataframe(df)
                            # --- Smart, question-aware visualization (force chart for demo) ---
                            intent = infer_intent(question)
                            if show_chart and df is not None and not df.empty and PLOTLY_AVAILABLE:
                                chart_reason = None
                                st.markdown("**Visualization:**")
                                # Single value: gauge
                                if df.shape == (1, 1):
                                    val = df.iloc[0, 0]
                                    label = df.columns[0]
                                    fig = go.Figure(go.Indicator(
                                        mode = "gauge+number+delta",
                                        value = val,
                                        title = {'text': label},
                                        delta = {'reference': 0},
                                        gauge = {
                                            'axis': {'range': [None, val*1.2]},
                                            'bar': {'color': "#00f2ff"},
                                            'steps': [
                                                {'range': [0, val*0.5], 'color': '#1a2233'},
                                                {'range': [val*0.5, val], 'color': '#7fd6ff'},
                                                {'range': [val, val*1.2], 'color': '#b2fefa'}
                                            ],
                                            'threshold': {'line': {'color': "#ff4b1f", 'width': 4}, 'thickness': 0.75, 'value': val}
                                        },
                                        number={'font': {'color': '#00f2ff', 'size': 48}}
                                    ))
                                    fig.update_layout(autosize=True, template="plotly_dark", margin=dict(l=20, r=20, t=60, b=20))
                                    st.plotly_chart(fig, use_container_width=True)
                                    chart_reason = "Gauge chart for single value."
                                # Two columns
                                elif df.shape[1] == 2:
                                    col0, col1 = df.columns
                                    # Force chart type for demo based on intent
                                    if intent == "trend":
                                        fig = px.line(df, x=col0, y=col1, color_discrete_sequence=["#00f2ff"])
                                        fig.update_xaxes(rangeslider_visible=True)
                                        fig.update_traces(line=dict(width=4))
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Line chart for trend/time series (forced by intent)."
                                    elif intent == "distribution":
                                        fig = px.histogram(df, x=col1, nbins=20, color_discrete_sequence=["#7fd6ff"])
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Histogram for distribution (forced by intent)."
                                    elif intent == "proportion":
                                        fig = px.sunburst(df, path=[col0], values=col1, color=col1, color_continuous_scale='Plasma')
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Sunburst for proportion/breakdown (forced by intent)."
                                    elif intent == "comparison":
                                        fig = px.scatter(df, x=col0, y=col1, color=col1, color_continuous_scale='Viridis', animation_frame=col0 if df[col0].nunique() < 50 else None)
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Animated scatter for comparison (forced by intent)."
                                    elif intent == "correlation":
                                        fig = px.scatter(df, x=col0, y=col1, color=col1, color_continuous_scale='Plasma', trendline="ols")
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Scatter with regression for correlation (forced by intent)."
                                    # Fallbacks
                                    elif pd.api.types.is_datetime64_any_dtype(df[col0]) and pd.api.types.is_numeric_dtype(df[col1]):
                                        fig = px.line(df, x=col0, y=col1, color_discrete_sequence=["#00f2ff"])
                                        fig.update_xaxes(rangeslider_visible=True)
                                        fig.update_traces(line=dict(width=4))
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Line chart for time series."
                                    elif pd.api.types.is_object_dtype(df[col0]) and pd.api.types.is_numeric_dtype(df[col1]):
                                        fig = px.sunburst(df, path=[col0], values=col1, color=col1, color_continuous_scale='Plasma')
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Sunburst for categorical breakdown."
                                    elif pd.api.types.is_numeric_dtype(df[col0]) and pd.api.types.is_numeric_dtype(df[col1]):
                                        fig = px.scatter(df, x=col0, y=col1, color=col1, color_continuous_scale='Plasma', trendline="ols")
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Scatter for numeric correlation."
                                    else:
                                        st.info("No suitable columns for chart. Data shown above.")
                                # Three columns: cat + 2 numeric
                                elif df.shape[1] == 3:
                                    cat_cols = df.select_dtypes(include='object').columns
                                    num_cols = df.select_dtypes(include='number').columns
                                    if len(cat_cols) >= 1 and len(num_cols) >= 2:
                                        cat = cat_cols[0]
                                        num1, num2 = num_cols[:2]
                                        fig = px.scatter(df, x=num1, y=num2, color=cat, size=num2, hover_name=cat, animation_frame=cat if df[cat].nunique() < 50 else None, color_continuous_scale='Plasma')
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Bubble chart for grouped numeric comparison."
                                    else:
                                        st.info("No suitable columns for chart. Data shown above.")
                                # More columns: parallel coordinates
                                elif df.shape[1] > 3:
                                    num_cols = df.select_dtypes(include='number').columns
                                    if len(num_cols) >= 2:
                                        st.info("Parallel coordinates plot of numeric columns:")
                                        fig = px.parallel_coordinates(df, dimensions=num_cols, color=num_cols[0], color_continuous_scale='Plasma')
                                        st.plotly_chart(fig, use_container_width=True)
                                        chart_reason = "Parallel coordinates for multi-numeric data."
                                    else:
                                        st.info("No suitable columns for chart. Data shown above.")
                                if chart_reason:
                                    st.caption(f"Chart type: {chart_reason}")
                        else:
                            st.info("No results found.")
                        if "sql" in data:
                            st.caption("SQL Query used:")
                            st.code(data["sql"], language="sql")
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Request failed: {e}")