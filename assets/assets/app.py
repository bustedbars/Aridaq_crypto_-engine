import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from aridaq_bridge import execute_aridaq_solver

# 1. Page Configuration
st.set_page_config(
    page_title="ARIDAQ Engine Interface",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Application Header
st.title("⚡ ARIDAQ PROTOCOL // SOLVER ENGINE")
st.caption("Non-Euclidean Constraint Optimization & Liquidity Manifold Interface")
st.markdown("---")

# 2. Main 3-Panel Layout
left_panel, center_panel, right_panel = st.columns([1.1, 2.0, 1.1], gap="medium")

# ==========================================
# LEFT PANEL: INPUTS & CONSTRAINTS
# ==========================================
with left_panel:
    st.subheader("1. Setup & Inputs")
    
    goal = st.text_area(
        "Optimization Goal", 
        value="Predict BTC 8 PM Geodesic Close & Liquidity Wall Absorption",
        height=70
    )
    
    st.markdown("#### Manifold Constraints")
    spot_anchor = st.number_input("Spot Price Anchor ($)", value=64886.0, step=10.0)
    volatility = st.slider("4H Volatility Scale Factor (σ)", 0.001, 0.030, 0.0082, format="%.4f")
    leverage_bias = st.select_slider("Derivatives Leverage Bias", options=["Bearish", "Neutral", "Bullish"], value="Bullish")
    
    st.markdown("#### Raw Data Sources")
    uploaded_files = st.file_uploader(
        "Drop L2 Depth / CSV / RSS Feeds", 
        accept_multiple_files=True,
        type=["csv", "json", "txt"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    engage_button = st.button("ENGAGE SOLVER ⚡")

# Initialize Session State for Results
if "solver_output" not in st.session_state:
    st.session_state["solver_output"] = None

if engage_button:
    with st.spinner("Executing non-Euclidean manifold transformation..."):
        constraints = {
            "spot_anchor": spot_anchor,
            "volatility": volatility,
            "bias": leverage_bias
        }
        # Execute Private Local Solver
        st.session_state["solver_output"] = execute_aridaq_solver(goal, constraints, uploaded_files)

output = st.session_state["solver_output"]

# ==========================================
# CENTER PANEL: VISUALS & WALL MAPS
# ==========================================
with center_panel:
    st.subheader("2. Liquidity Walls & Depth Manifold")
    
    if output is None:
        st.info("Input parameters on the Left Panel and click **ENGAGE SOLVER** to render execution analytics.")
    else:
        df = output["df_depth"]
        
        # Build Order Book Liquidity Depth Chart
        fig = go.Figure()
        
        # Bids (Buy Depth)
        fig.add_trace(go.Scatter(
            x=df["Price"], y=df["Bid_Depth"],
            mode='lines', fill='tozeroy',
            name='Bid Liquidity (Support)',
            line=dict(color='#00E676', width=2),
            fillcolor='rgba(0, 230, 118, 0.15)'
        ))
        
        # Asks (Sell Depth)
        fig.add_trace(go.Scatter(
            x=df["Price"], y=df["Ask_Depth"],
            mode='lines', fill='tozeroy',
            name='Ask Liquidity (Resistance)',
            line=dict(color='#FFB7D5', width=2),
            fillcolor='rgba(255, 183, 213, 0.2)'
        ))
        
        # Spot Line
        fig.add_vline(x=spot_anchor, line_dash="dash", line_color="#FFFFFF", annotation_text="Spot Anchor")
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=30, b=10),
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key Metrics Row
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Geodesic Target Price", f"${output['target_price']:,}")
        with col_b:
            st.metric("Major Wall Detected", f"${output['liquidation_wall_price']:,}", f"{output['liquidation_wall_vol']} BTC")

# ==========================================
# RIGHT PANEL: PREDICTION PROBABILITIES
# ==========================================
with right_panel:
    st.subheader("3. Execution Edge")
    
    if output is None:
        st.warning("Standing by for solver engagement...")
    else:
        st.markdown("#### Polymarket Target Edge")
        
        st.metric(
            label="Aridaq Model Probability", 
            value=f"{output['model_prob']}%",
            delta=f"+{output['arb_edge']}% vs Crowd"
        )
        
        st.metric(
            label="Polymarket Crowd Implied", 
            value=f"{output['poly_prob']}%"
        )
        
        st.markdown("---")
        st.markdown("#### Execution Verdict")
        
        if output['arb_edge'] > 10.0:
            st.success(f"**POSITIVE ARBITRAGE DIVERGENCE DETECTED**\n\nModel indicates a **{output['arb_edge']}% edge** over market consensus. Favorable odds for target bracket.")
        else:
            st.info("Market pricing aligned with model bounds. Low divergence window.")
            
        st.caption("Execution Log: All operations computed locally in isolated memory space.")
