import streamlit as st
import requests
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict

# API Base URL
API_BASE_URL = "http://127.0.0.1:5000"

# Page config
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Title
st.title("💰 Personal Expense Tracker")
st.markdown("---")

# Helper function to call API
def call_api(endpoint, method="GET", data=None, params=None):
    """Helper function to make API calls"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Please make sure Flask API is running on port 5000.")
        st.code("python app.py", language="bash")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ API request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# Fetch categories from API
def get_categories():
    """Fetch valid categories from API"""
    response = call_api("/categories")
    if response and response.status_code == 200:
        return response.json().get("categories", [])
    return ['FOOD', 'RENT', 'TRANSPORT', 'GROCERIES', 'UTILITIES', 
            'ENTERTAINMENT', 'HEALTH', 'EDUCATION', 'SHOPPING', 'TRAVEL', 'OTHER']

# Create two columns for layout
col1, col2 = st.columns([1, 2])

# LEFT COLUMN - Add Expense Form
with col1:
    st.header("➕ Add New Expense")
    
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
        
        categories = get_categories()
        category = st.selectbox("Category", categories)
        
        description = st.text_input("Description (optional)")
        
        expense_date = st.date_input("Date", value=date.today(), max_value=date.today())
        
        submit_button = st.form_submit_button("💾 Add Expense", use_container_width=True)
        
        if submit_button:
            # Prepare data
            expense_data = {
                "amount": amount,
                "category": category,
                "description": description if description else "",
                "date": expense_date.strftime("%Y-%m-%d")
            }
            
            # Call API
            response = call_api("/expenses", method="POST", data=expense_data)
            
            if response:
                if response.status_code in [200, 201]:
                    result = response.json()
                    if result.get("status") == "duplicate":
                        st.warning("⚠️ This expense was already recorded recently!")
                    else:
                        st.success("✅ Expense added successfully!")
                    st.rerun()
                else:
                    error_msg = response.json().get("error", "Unknown error")
                    st.error(f"❌ Error: {error_msg}")

# RIGHT COLUMN - View Expenses
with col2:
    st.header("📊 Expense List")
    
    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
    
    with filter_col1:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All"] + categories,
            key="filter_category"
        )
    
    with filter_col2:
        sort_order = st.selectbox(
            "Sort by Date",
            ["Newest First", "Oldest First"],
            key="sort_order"
        )
    
    with filter_col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Prepare API parameters
    params = {}
    if filter_category != "All":
        params["category"] = filter_category
    if sort_order == "Newest First":
        params["sort"] = "date_desc"
    
    # Fetch expenses from API
    response = call_api("/expenses", params=params)
    
    if response and response.status_code == 200:
        data = response.json()
        expenses = data.get("expenses", [])
        total = data.get("total", 0)
        count = data.get("count", 0)
        
        # Display total
        st.metric(label="Total Expenses", value=f"₹ {total:,.2f}", delta=f"{count} expenses")
        
        # Display expenses
        if expenses:
            # Convert to DataFrame for better display
            df = pd.DataFrame(expenses)
            
            # Display expenses with delete option
            st.write("#### Expense Records")
            
            for idx, expense in enumerate(expenses):
                with st.container():
                    col_date, col_cat, col_amt, col_desc, col_del = st.columns([2, 2, 1.5, 3, 1])
                    
                    with col_date:
                        st.text(expense['expense_date'])
                    
                    with col_cat:
                        st.text(expense['category'])
                    
                    with col_amt:
                        st.text(f"₹ {expense['amount']:,.2f}")
                    
                    with col_desc:
                        st.text(expense.get('description', '-') or '-')
                    
                    with col_del:
                        if st.button("🗑️", key=f"delete_{expense['id']}", help="Delete this expense"):
                            # Call delete API
                            delete_response = call_api(f"/expenses/{expense['id']}", method="DELETE")
                            
                            if delete_response and delete_response.status_code == 200:
                                st.success("✅ Deleted!")
                                st.rerun()
                            elif delete_response and delete_response.status_code == 404:
                                st.error("❌ Expense not found")
                            else:
                                st.error("❌ Failed to delete")
                    
                    if idx < len(expenses) - 1:
                        st.divider()
            
            # Download option
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 No expenses found. Add your first expense!")
    
    elif response:
        st.error(f"❌ Error fetching expenses: {response.json().get('error', 'Unknown error')}")

# CHARTS SECTION (Full Width)
st.markdown("---")
st.header("📈 Analytics & Insights")

# Fetch all expenses for charts (no filters)
chart_response = call_api("/expenses", params={"sort": "date_desc"})

if chart_response and chart_response.status_code == 200:
    chart_data = chart_response.json()
    all_expenses = chart_data.get("expenses", [])
    
    if all_expenses:
        # Convert to DataFrame
        df_all = pd.DataFrame(all_expenses)
        df_all['expense_date'] = pd.to_datetime(df_all['expense_date'])
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)
        
        # PIE CHART - Category-wise Breakdown
        with chart_col1:
            st.subheader("🥧 Expenses by Category")
            
            # Group by category and sum amounts
            category_totals = df_all.groupby('category')['amount'].sum().reset_index()
            category_totals = category_totals.sort_values('amount', ascending=False)
            
            # Create pie chart
            fig_pie = px.pie(
                category_totals,
                values='amount',
                names='category',
                title='Category Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Show category breakdown table
            category_totals['Percentage'] = (category_totals['amount'] / category_totals['amount'].sum() * 100).round(2)
            category_totals.columns = ['Category', 'Total (₹)', 'Percentage (%)']
            category_totals['Total (₹)'] = category_totals['Total (₹)'].apply(lambda x: f"₹ {x:,.2f}")
            st.dataframe(category_totals, use_container_width=True, hide_index=True)
        
        # LINE CHART - Monthly Expenses Trend
        with chart_col2:
            st.subheader("📊 Monthly Expense Trend")
            
            # Extract year-month and group
            df_all['year_month'] = df_all['expense_date'].dt.to_period('M').astype(str)
            monthly_totals = df_all.groupby('year_month')['amount'].sum().reset_index()
            monthly_totals = monthly_totals.sort_values('year_month')
            
            # Create line chart
            fig_line = go.Figure()
            
            fig_line.add_trace(go.Scatter(
                x=monthly_totals['year_month'],
                y=monthly_totals['amount'],
                mode='lines+markers',
                name='Monthly Expenses',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Total: ₹%{y:,.2f}<extra></extra>'
            ))
            
            fig_line.update_layout(
                title='Monthly Spending Pattern',
                xaxis_title='Month',
                yaxis_title='Amount (₹)',
                hovermode='x unified',
                showlegend=False
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Show monthly breakdown table
            monthly_totals.columns = ['Month', 'Total (₹)']
            monthly_totals['Total (₹)'] = monthly_totals['Total (₹)'].apply(lambda x: f"₹ {x:,.2f}")
            st.dataframe(monthly_totals, use_container_width=True, hide_index=True)
        
        # Additional Insights
        st.markdown("---")
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            highest_category = category_totals.iloc[0]['Category']
            st.metric(
                "💸 Highest Spending Category",
                highest_category,
                delta=category_totals.iloc[0]['Percentage (%)']
            )
        
        with insight_col2:
            avg_expense = df_all['amount'].mean()
            st.metric(
                "📊 Average Expense",
                f"₹ {avg_expense:,.2f}"
            )
        
        with insight_col3:
            if len(monthly_totals) >= 2:
                last_month = float(monthly_totals.iloc[-1]['Total (₹)'].replace('₹', '').replace(',', ''))
                prev_month = float(monthly_totals.iloc[-2]['Total (₹)'].replace('₹', '').replace(',', ''))
                change = ((last_month - prev_month) / prev_month * 100)
                st.metric(
                    "📈 Month-over-Month Change",
                    f"{change:+.1f}%",
                    delta=f"₹ {last_month - prev_month:,.2f}"
                )
            else:
                st.metric("📈 Month-over-Month Change", "N/A")
    
    else:
        st.info("📊 Add some expenses to see analytics and charts!")

# Footer
st.markdown("---")
st.caption("💡 Tip: Make sure the Flask API is running (`python app.py`) before using this interface.")