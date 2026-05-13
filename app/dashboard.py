import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS STYLING
# ---------------------------------------------------
st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

h1 {
    color: #2c3e50;
    font-weight: 700;
}

h2, h3 {
    color: #34495e;
}

[data-testid="metric-container"] {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    border-left: 5px solid #1f77b4;
}

.stPlotlyChart {
    background-color: white;
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

section[data-testid="stSidebar"] {
    background-color: #2c3e50;
}

section[data-testid="stSidebar"] * {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------
conn = sqlite3.connect('data/ecommerce.db')

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.title("📌 Dashboard Filters")

month_query = """
SELECT DISTINCT
    strftime('%Y-%m', order_purchase_timestamp) AS month
FROM orders
ORDER BY month
"""

months_df = pd.read_sql(month_query, conn)

selected_month = st.sidebar.selectbox(
    "Select Month",
    months_df['month']
)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown("""
# 📊 E-Commerce Analytics Report

Modern business intelligence dashboard powered by:
- Python
- SQL
- Machine Learning
- Streamlit
- Plotly
""")

st.markdown("---")

# ---------------------------------------------------
# KPI QUERIES
# ---------------------------------------------------

revenue_query = f"""
SELECT ROUND(SUM(p.payment_value), 2) AS revenue
FROM orders o
JOIN payments p
ON o.order_id = p.order_id
WHERE strftime('%Y-%m', o.order_purchase_timestamp) = '{selected_month}'
"""

orders_query = f"""
SELECT COUNT(*) AS total_orders
FROM orders
WHERE strftime('%Y-%m', order_purchase_timestamp) = '{selected_month}'
"""

aov_query = f"""
SELECT ROUND(AVG(p.payment_value), 2) AS aov
FROM orders o
JOIN payments p
ON o.order_id = p.order_id
WHERE strftime('%Y-%m', o.order_purchase_timestamp) = '{selected_month}'
"""

revenue = pd.read_sql(revenue_query, conn)
orders = pd.read_sql(orders_query, conn)
aov = pd.read_sql(aov_query, conn)

# ---------------------------------------------------
# KPI ROW
# ---------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💰 Total Revenue",
        f"${revenue['revenue'][0]:,.2f}"
    )

with col2:
    st.metric(
        "📦 Total Orders",
        int(orders['total_orders'][0])
    )

with col3:
    st.metric(
        "🛒 Avg Order Value",
        f"${aov['aov'][0]:,.2f}"
    )

st.markdown("##")

# ---------------------------------------------------
# MONTHLY REVENUE TREND
# ---------------------------------------------------
monthly_query = """
SELECT 
    strftime('%Y-%m', o.order_purchase_timestamp) AS month,
    ROUND(SUM(p.payment_value), 2) AS revenue
FROM orders o
JOIN payments p
ON o.order_id = p.order_id
GROUP BY month
ORDER BY month
"""

monthly_revenue = pd.read_sql(monthly_query, conn)

fig1 = px.line(
    monthly_revenue,
    x='month',
    y='revenue',
    markers=True,
    title='📈 Monthly Revenue Trend'
)

fig1.update_layout(
    template='plotly_white',
    height=450
)

st.plotly_chart(fig1, use_container_width=True)

# ---------------------------------------------------
# TWO COLUMN SECTION
# ---------------------------------------------------
left_col, right_col = st.columns(2)

# ---------------------------------------------------
# TOP CATEGORIES
# ---------------------------------------------------
with left_col:

    category_query = """
    SELECT 
        p.product_category_name,
        COUNT(oi.order_id) AS total_sales
    FROM order_items oi
    JOIN products p
    ON oi.product_id = p.product_id
    GROUP BY p.product_category_name
    ORDER BY total_sales DESC
    LIMIT 10
    """

    top_categories = pd.read_sql(category_query, conn)

    fig2 = px.bar(
        top_categories,
        x='total_sales',
        y='product_category_name',
        orientation='h',
        title='🏆 Top Product Categories'
    )

    fig2.update_layout(
        template='plotly_white',
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# PAYMENT METHOD
# ---------------------------------------------------
with right_col:

    payment_query = """
    SELECT 
        payment_type,
        COUNT(*) AS total_transactions
    FROM payments
    GROUP BY payment_type
    """

    payment_df = pd.read_sql(payment_query, conn)

    fig3 = px.pie(
        payment_df,
        names='payment_type',
        values='total_transactions',
        title='💳 Payment Distribution'
    )

    fig3.update_layout(
        template='plotly_white',
        height=500
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------------
# CUSTOMER REVIEW ANALYSIS
# ---------------------------------------------------
review_query = """
SELECT 
    review_score,
    COUNT(*) AS total_reviews
FROM reviews
GROUP BY review_score
ORDER BY review_score
"""

review_df = pd.read_sql(review_query, conn)

fig4 = px.bar(
    review_df,
    x='review_score',
    y='total_reviews',
    title='⭐ Customer Review Analysis'
)

fig4.update_layout(
    template='plotly_white',
    height=400
)

st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------
# CUSTOMER SEGMENTATION
# ---------------------------------------------------
st.subheader("👥 Customer Segmentation")

rfm_query = """
SELECT 
    c.customer_unique_id,
    COUNT(o.order_id) AS frequency,
    ROUND(SUM(p.payment_value),2) AS monetary
FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
JOIN payments p
ON o.order_id = p.order_id
GROUP BY c.customer_unique_id
LIMIT 500
"""

rfm_df = pd.read_sql(rfm_query, conn)

fig5 = px.scatter(
    rfm_df,
    x='frequency',
    y='monetary',
    title='Customer Segments'
)

fig5.update_layout(
    template='plotly_white',
    height=500
)

st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------
# FORECASTING SECTION
# ---------------------------------------------------
st.subheader("🔮 Revenue Forecast")

monthly_revenue['Month_Index'] = range(len(monthly_revenue))

X = monthly_revenue[['Month_Index']]
y = monthly_revenue['revenue']

model = LinearRegression()
model.fit(X, y)

future_months = pd.DataFrame({
    'Month_Index': range(
        len(monthly_revenue),
        len(monthly_revenue) + 6
    )
})

future_predictions = model.predict(future_months)

future_df = pd.DataFrame({
    'Future_Month': [
        'Month 1',
        'Month 2',
        'Month 3',
        'Month 4',
        'Month 5',
        'Month 6'
    ],
    'Forecasted_Revenue': future_predictions
})

fig6 = px.line(
    future_df,
    x='Future_Month',
    y='Forecasted_Revenue',
    markers=True,
    title='Next 6 Months Forecast'
)

fig6.update_layout(
    template='plotly_white',
    height=400
)

st.plotly_chart(fig6, use_container_width=True)

# ---------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------
st.subheader("📌 Executive Summary")

st.markdown("""
### Key Business Findings

✅ Revenue demonstrates consistent long-term growth trends.

✅ Credit cards are the dominant customer payment method.

✅ Certain product categories significantly outperform others.

✅ Customer satisfaction remains strong with high review scores.

✅ Revenue forecasting suggests future business expansion.

✅ Customer segmentation indicates multiple purchasing behaviors.
""")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")

st.caption(
    "Built with Python, SQL, Streamlit, Plotly, and Machine Learning"
)