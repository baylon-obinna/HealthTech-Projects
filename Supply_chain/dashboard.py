import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime

# DATA CLEANING

# ── 1. LOAD THE DATA ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_excel(os.path.join(BASE_DIR, "pharmacy_inventory.xlsx"))

# ── 2. FIX DATE FORMAT ────────────────────────────────────────────────────────
df["expiry_date"]   = pd.to_datetime(df["expiry_date"])
df["date_received"] = pd.to_datetime(df["date_received"])

# ── 3. CALCULATE DAYS TO EXPIRY ───────────────────────────────────────────────
today = pd.Timestamp(datetime.today().date())
df["days_to_expiry"] = (df["expiry_date"] - today).dt.days

# ── 4. FLAG EXPIRY STATUS ─────────────────────────────────────────────────────
def flag_status(days):
    if days < 0:
        return "Expired"
    elif days <= 30:
        return "Critical"
    elif days <= 90:
        return "Warning"
    else:
        return "Safe"

df["status"] = df["days_to_expiry"].apply(flag_status)

# ── 5. CALCULATE STOCK VALUE AT RISK ──────────────────────────────────────────
# Value at risk = stock that is expired or critical
at_risk = df[df["status"].isin(["Expired", "Critical"])]
value_at_risk = at_risk["total_value_ngn"].sum()

# ── 6. GROUP BY CATEGORY — which categories have the most risk ────────────────
category_risk = (
    df.groupby(["category", "status"])["total_value_ngn"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

# ── 7. PRINT SUMMARY REPORT ───────────────────────────────────────────────────
print("=" * 55)
print("   NIGERIA PHARMACY — EXPIRY ANALYSIS REPORT")
print("=" * 55)

print(f"\n📦 Total SKUs (batches):     {len(df)}")
print(f"💊 Unique drugs:             {df['drug_name'].nunique()}")
print(f"🏪 Locations tracked:        {df['location'].nunique()}")

print("\n📊 STATUS BREAKDOWN")
print("-" * 35)
status_counts = df["status"].value_counts()
for status, count in status_counts.items():
    print(f"   {status:<12} {count:>4} batches")

print("\n💰 STOCK VALUE AT RISK")
print("-" * 35)
print(f"   Expired + Critical stock:  ₦{value_at_risk:>12,.2f}")
total_value = df["total_value_ngn"].sum()
pct = (value_at_risk / total_value) * 100
print(f"   Total inventory value:     ₦{total_value:>12,.2f}")
print(f"   % of inventory at risk:    {pct:.1f}%")

print("\n🏷️  TOP 5 DRUGS MOST AT RISK (by value)")
print("-" * 35)
top_risk = (
    at_risk.groupby("drug_name")["total_value_ngn"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
for drug, val in top_risk.items():
    print(f"   {drug[:35]:<35}  ₦{val:>10,.0f}")

print("\n📍 RISK BY LOCATION")
print("-" * 35)
loc_risk = (
    at_risk.groupby("location")["total_value_ngn"]
    .sum()
    .sort_values(ascending=False)
)
for loc, val in loc_risk.items():
    print(f"   {loc:<25}  ₦{val:>10,.0f}")

print("\n" + "=" * 55)
print("✅ Analysis complete.")
print("=" * 55)

# ── 8. EXPORT CLEAN FILE FOR DASHBOARD ───────────────────────────────────────
df.to_csv("inventory_clean.csv", index=False)
print("\n📁 inventory_clean.csv saved.")
# ###

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drug Expiry Dashboard",
    page_icon="💊",
    layout="wide",
)

# ── STYLING ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background-color: #0F1117; }

.metric-card {
    background: #1A1D27;
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 4px solid;
    margin-bottom: 8px;
}
.metric-card.red   { border-color: #FF4B4B; }
.metric-card.orange{ border-color: #FF8C00; }
.metric-card.yellow{ border-color: #FFD700; }
.metric-card.green { border-color: #00C48C; }
.metric-card.blue  { border-color: #4B9EFF; }

.metric-label { font-size: 11px; font-weight: 600; letter-spacing: 1.2px;
                text-transform: uppercase; color: #6B7280; margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; color: #F9FAFB; line-height: 1; }
.metric-sub   { font-size: 12px; color: #9CA3AF; margin-top: 4px; }

.section-header {
    font-size: 13px; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; color: #6B7280;
    border-bottom: 1px solid #1F2937;
    padding-bottom: 8px; margin: 24px 0 16px 0;
}
.status-badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600; font-family: 'DM Mono', monospace;
}
.badge-expired  { background:#FF4B4B22; color:#FF4B4B; }
.badge-critical { background:#FF8C0022; color:#FF8C00; }
.badge-warning  { background:#FFD70022; color:#FFD700; }
.badge-safe     { background:#00C48C22; color:#00C48C; }

div[data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("inventory_clean.csv")
    df["expiry_date"]   = pd.to_datetime(df["expiry_date"])
    df["date_received"] = pd.to_datetime(df["date_received"])
    today = pd.Timestamp(datetime.today().date())
    df["days_to_expiry"] = (df["expiry_date"] - today).dt.days
    def flag(d):
        if d < 0:   return "Expired"
        elif d <= 30:  return "Critical"
        elif d <= 90:  return "Warning"
        else:          return "Safe"
    df["status"] = df["days_to_expiry"].apply(flag)
    return df

df = load_data()
today = pd.Timestamp(datetime.today().date())

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    all_locations = ["All Locations"] + sorted(df["location"].unique().tolist())
    selected_location = st.selectbox("Location", all_locations)

    all_categories = ["All Categories"] + sorted(df["category"].unique().tolist())
    selected_category = st.multiselect("Category", all_categories[1:],
                                        default=all_categories[1:])

    status_filter = st.multiselect(
        "Status",
        ["Expired", "Critical", "Warning", "Safe"],
        default=["Expired", "Critical", "Warning", "Safe"]
    )
    st.divider()
    st.markdown("<span style='color:#4B5563;font-size:12px'>Drug Expiry & Inventory</span>", unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_location != "All Locations":
    filtered = filtered[filtered["location"] == selected_location]
if selected_category:
    filtered = filtered[filtered["category"].isin(selected_category)]
if status_filter:
    filtered = filtered[filtered["status"].isin(status_filter)]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("## 💊 Drug Expiry & Inventory Dashboard")
st.markdown(f"<span style='color:#6B7280;font-size:13px'>Last updated: {today.strftime('%d %B %Y')}</span>",
            unsafe_allow_html=True)

st.markdown("---")

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
at_risk_df    = filtered[filtered["status"].isin(["Expired", "Critical"])]
value_at_risk = at_risk_df["total_value_ngn"].sum()
total_value   = filtered["total_value_ngn"].sum()
pct_risk      = (value_at_risk / total_value * 100) if total_value > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""<div class='metric-card red'>
        <div class='metric-label'>Value at Risk</div>
        <div class='metric-value'>₦{value_at_risk/1_000_000:.1f}M</div>
        <div class='metric-sub'>{pct_risk:.1f}% of inventory</div>
    </div>""", unsafe_allow_html=True)

with c2:
    expired_count = len(filtered[filtered["status"] == "Expired"])
    st.markdown(f"""<div class='metric-card orange'>
        <div class='metric-label'>Expired Batches</div>
        <div class='metric-value'>{expired_count}</div>
        <div class='metric-sub'>Must be quarantined</div>
    </div>""", unsafe_allow_html=True)

with c3:
    critical_count = len(filtered[filtered["status"] == "Critical"])
    st.markdown(f"""<div class='metric-card yellow'>
        <div class='metric-label'>Critical (≤30 days)</div>
        <div class='metric-value'>{critical_count}</div>
        <div class='metric-sub'>Urgent action needed</div>
    </div>""", unsafe_allow_html=True)

with c4:
    warning_count = len(filtered[filtered["status"] == "Warning"])
    st.markdown(f"""<div class='metric-card blue'>
        <div class='metric-label'>Warning (31–90 days)</div>
        <div class='metric-value'>{warning_count}</div>
        <div class='metric-sub'>Plan returns or promos</div>
    </div>""", unsafe_allow_html=True)

with c5:
    total_skus = len(filtered)
    st.markdown(f"""<div class='metric-card green'>
        <div class='metric-label'>Total Batches</div>
        <div class='metric-value'>{total_skus}</div>
        <div class='metric-sub'>{filtered['drug_name'].nunique()} unique drugs</div>
    </div>""", unsafe_allow_html=True)

# ── ROW 2: CHARTS ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📊 Expiry Analysis</div>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 1])

COLORS = {
    "Expired":  "#FF4B4B",
    "Critical": "#FF8C00",
    "Warning":  "#FFD700",
    "Safe":     "#00C48C",
}

# -- Monthly expiry bar chart
with col_left:
    future = filtered[filtered["days_to_expiry"].between(0, 180)].copy()
    if not future.empty:
        future["expiry_month"] = future["expiry_date"].dt.to_period("M").astype(str)
        monthly = (future.groupby(["expiry_month", "status"])["quantity"]
                   .sum().reset_index())
        monthly = monthly.sort_values("expiry_month")
        fig_bar = px.bar(
            monthly, x="expiry_month", y="quantity", color="status",
            color_discrete_map=COLORS,
            labels={"expiry_month": "", "quantity": "Units", "status": ""},
            title="Units Expiring — Next 6 Months",
            barmode="stack",
        )
        fig_bar.update_layout(
            plot_bgcolor="#1A1D27", paper_bgcolor="#1A1D27",
            font=dict(color="#9CA3AF", family="DM Sans"),
            title_font=dict(color="#F9FAFB", size=14),
            legend=dict(
                orientation="h", yanchor="top", y=-0.18,
                xanchor="left", x=0,
                font=dict(size=11),
            ),
            xaxis=dict(gridcolor="#2D3748"),
            yaxis=dict(gridcolor="#2D3748"),
            margin=dict(t=45, b=60, l=0, r=0),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No items expiring in the next 6 months for this filter.")

# -- Status donut
with col_right:
    status_counts = filtered["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig_donut = px.pie(
        status_counts, values="count", names="status",
        color="status", color_discrete_map=COLORS,
        hole=0.5, title="Stock Status Breakdown",
    )
    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(color="#F9FAFB", size=11),
        insidetextorientation="radial",
    )
    fig_donut.update_layout(
        plot_bgcolor="#1A1D27", paper_bgcolor="#1A1D27",
        font=dict(color="#9CA3AF", family="DM Sans"),
        title_font=dict(color="#F9FAFB", size=14),
        showlegend=False,
        margin=dict(t=50, b=20, l=20, r=20),
        height=340,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ── ROW 3: RISK BY LOCATION + TOP DRUGS ───────────────────────────────────────
st.markdown("<div class='section-header'>📍 Risk Breakdown</div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    loc_risk = (at_risk_df.groupby("location")["total_value_ngn"]
                .sum().sort_values().reset_index())
    loc_risk.columns = ["location", "value"]
    fig_loc = px.bar(
        loc_risk, x="value", y="location", orientation="h",
        title="₦ At-Risk Value by Location",
        labels={"value": "Value (₦)", "location": ""},
        color_discrete_sequence=["#FF4B4B"],
    )
    fig_loc.update_layout(
        plot_bgcolor="#1A1D27", paper_bgcolor="#1A1D27",
        font=dict(color="#9CA3AF", family="DM Sans"),
        title_font=dict(color="#F9FAFB", size=14),
        xaxis=dict(gridcolor="#2D3748", tickprefix="₦", tickformat=",.0f"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=50, b=20, l=0, r=0),
    )
    st.plotly_chart(fig_loc, use_container_width=True)

with col_b:
    top_drugs = (at_risk_df.groupby("drug_name")["total_value_ngn"]
                 .sum().sort_values(ascending=False).head(8).reset_index())
    top_drugs.columns = ["drug", "value"]
    fig_drugs = px.bar(
        top_drugs, x="value", y="drug", orientation="h",
        title="Top 8 Drugs at Risk (₦ Value)",
        labels={"value": "Value (₦)", "drug": ""},
        color_discrete_sequence=["#FF8C00"],
    )
    fig_drugs.update_layout(
        plot_bgcolor="#1A1D27", paper_bgcolor="#1A1D27",
        font=dict(color="#9CA3AF", family="DM Sans"),
        title_font=dict(color="#F9FAFB", size=14),
        xaxis=dict(gridcolor="#2D3748", tickprefix="₦", tickformat=",.0f"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=50, b=20, l=0, r=0),
    )
    st.plotly_chart(fig_drugs, use_container_width=True)

# ── ROW 4: CATEGORY HEATMAP ───────────────────────────────────────────────────
st.markdown("<div class='section-header'>🏷️ Category Risk Heatmap</div>",
            unsafe_allow_html=True)

cat_pivot = (filtered.groupby(["category", "status"])["total_value_ngn"]
             .sum().unstack(fill_value=0).reset_index())
status_order = [s for s in ["Expired","Critical","Warning","Safe"] if s in cat_pivot.columns]
cat_pivot["total"] = cat_pivot[status_order].sum(axis=1)
cat_pivot = cat_pivot.sort_values("total", ascending=False)

fig_heat = go.Figure()
for status in status_order:
    if status in cat_pivot.columns:
        fig_heat.add_trace(go.Bar(
            name=status, x=cat_pivot["category"], y=cat_pivot[status],
            marker_color=COLORS[status],
        ))

fig_heat.update_layout(
    barmode="stack",
    plot_bgcolor="#1A1D27", paper_bgcolor="#1A1D27",
    font=dict(color="#9CA3AF", family="DM Sans"),
    title=dict(text="Total Inventory Value by Category & Status", font=dict(color="#F9FAFB", size=14)),
    xaxis=dict(gridcolor="#2D3748", tickangle=-30),
    yaxis=dict(gridcolor="#2D3748", tickprefix="₦", tickformat=",.0f"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(t=60, b=60, l=0, r=0),
    height=380,
)
st.plotly_chart(fig_heat, use_container_width=True)

# ── ROW 5: DATA TABLE ─────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📋 Inventory Detail</div>", unsafe_allow_html=True)

search = st.text_input("🔎 Search drug name", placeholder="e.g. Metformin, Amlodipine...")

table_df = filtered.copy()
if search:
    table_df = table_df[table_df["drug_name"].str.contains(search, case=False, na=False)]

# Sort by urgency
status_order_sort = {"Expired": 0, "Critical": 1, "Warning": 2, "Safe": 3}
table_df["sort_key"] = table_df["status"].map(status_order_sort)
table_df = table_df.sort_values(["sort_key", "days_to_expiry"]).drop(columns="sort_key")

display_cols = ["drug_name","category","batch_number","quantity",
                "total_value_ngn","expiry_date","days_to_expiry","status","location","supplier"]

def color_status(val):
    colors = {
        "Expired":  "background-color:#FF4B4B22; color:#FF4B4B; font-weight:600",
        "Critical": "background-color:#FF8C0022; color:#FF8C00; font-weight:600",
        "Warning":  "background-color:#FFD70022; color:#FFD700; font-weight:600",
        "Safe":     "background-color:#00C48C22; color:#00C48C; font-weight:600",
    }
    return colors.get(val, "")

styled = (table_df[display_cols]
          .rename(columns={
              "drug_name": "Drug", "category": "Category",
              "batch_number": "Batch", "quantity": "Qty",
              "total_value_ngn": "Value (₦)", "expiry_date": "Expiry Date",
              "days_to_expiry": "Days Left", "status": "Status",
              "location": "Location", "supplier": "Supplier",
          })
          .style
          .map(color_status, subset=["Status"])
          .format({"Value (₦)": "₦{:,.0f}", "Expiry Date": lambda x: x.strftime("%d %b %Y") if pd.notna(x) else ""})
         )

st.dataframe(styled, use_container_width=True, height=400)

st.markdown(f"<div style='color:#6B7280;font-size:12px;margin-top:4px'>"
            f"Showing {len(table_df)} of {len(filtered)} records</div>",
            unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#374151;font-size:12px'>"
    "Built with Python + Streamlit"
    "</div>", unsafe_allow_html=True
)