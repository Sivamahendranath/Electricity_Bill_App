import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bill_calculator import BillCalculator
import base64
from io import BytesIO
import datetime
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
import requests
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Electricity Bill Calculator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo URL 
LOGO_URL = "https://mir-s3-cdn-cf.behance.net/projects/404/d158eb92277443.Y3JvcCwxOTk5LDE1NjQsMCwyMTc.jpg"

# Custom CSS for better styling
def local_css():
    st.markdown("""
    <style>
    .main {
        padding: 2rem 1rem;
        background-color: #f0f8ff;
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    h1 {
        color: #963366;
        text-align: center;
        padding-bottom: 15px;
        border-bottom: 2px solid #003366;
        margin-bottom: 30px;
    }
    h2 {
        color: #ccff66;
        margin-top: 20px;
    }
    h3 {
        color: #ff69b4;
    }
    .css-1v3fvcr {
        background-color:rgb(230, 246, 92);
    }
    .stMetric {
        background-color:rgb(213, 130, 243);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .info-box {
        background-color:rgb(43, 182, 247);
        border-left: 5px solid #007bff;
        padding: 15px;
        margin: 10px 0;
    }
    .download-btn {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 10px 2px;
        border-radius: 5px;
        cursor: pointer;
    }
    .due-date-warning {
        color: #ff0000;
        font-weight: bold;
    }
    .payment-info {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        margin: 15px 0;
    }
    .bill-history {
        max-height: 300px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)

def download_and_save_logo():
    """Download logo from URL and save it temporarily"""
    try:
        response = requests.get(LOGO_URL)
        if response.status_code == 200:
            temp_dir = tempfile.gettempdir()
            logo_path = os.path.join(temp_dir, "ap_logo.jpg")
            with open(logo_path, "wb") as f:
                f.write(response.content)
            return logo_path
        else:
            return None
    except Exception as e:
        print(f"Error downloading logo: {e}")
        return None

def generate_pdf(data):
    """Generate a PDF bill with logo and bill details"""
    # Create a PDF buffer
    buffer = BytesIO()
    
    # Create the PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add logo
    logo_path = download_and_save_logo()
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 40, height - 120, width=100, height=80)
        except Exception as e:
            print(f"Error adding logo to PDF: {e}")
    
    # Add header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(150, height - 80, "Electricity Bill")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 140, "Bill Invoice")
    
    # Add date
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 160, f"Bill Date: {data['Bill_Date']}")
    c.drawString(40, height - 180, f"Due Date: {data['Due_Date']}")
    c.drawString(40, height - 200, f"Invoice #: AP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    # Customer information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 240, "Customer Information")
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 260, f"Customer Name: {data['Customer_Name']}")
    c.drawString(40, height - 280, f"Service ID: {data['Service_ID']}")
    c.drawString(40, height - 300, f"Customer Type: {data['Customer_Type']}")
    
    # Billing information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 340, "Billing Information")
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 360, f"Previous Reading: {data['Previous_Reading']} kWh")
    c.drawString(40, height - 380, f"Current Reading: {data['Current_Reading']} kWh")
    c.drawString(40, height - 400, f"Units Consumed: {data['Units_Consumed']} kWh")
    
    y_position = 400
    
    if "Peak_Hour_Units" in data:
        y_position += 20
        c.drawString(40, height - y_position, f"Peak Hour Units: {data['Peak_Hour_Units']} kWh")
    
    # Draw a line
    y_position += 20
    c.line(40, height - y_position, width - 40, height - y_position)
    
    # Bill summary
    y_position += 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - y_position, "Bill Summary")
    c.setFont("Helvetica", 12)
    y_position += 20
    c.drawString(40, height - y_position, f"Net Bill: ₹{data['Net_Bill']}")
    y_position += 20
    c.drawString(40, height - y_position, f"Service Charge (5%): ₹{data['Service_Charge']}")
    y_position += 20
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - y_position, f"Total Bill: ₹{data['Total_Bill']}")
    
    # Late payment section
    # y_position += 40
    # c.setFont("Helvetica-Bold", 14)
    # c.drawString(40, height - y_position, "Payment Information")
    # c.setFont("Helvetica", 12)
    # y_position += 20
    # c.drawString(40, height - y_position, f"Payment Due Date: {data['Due_Date']}")
    # y_position += 20
    # c.drawString(40, height - y_position, f"Late Payment Fee (2%): ₹{data['Late_Fee']}")
    # y_position += 20
    # c.setFont("Helvetica-Bold", 12)
    # c.drawString(40, height - y_position, f"Amount After Due Date: ₹{data['Amount_After_Due_Date']}")
    
    # Payment methods section
    y_position += 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - y_position, "Payment Methods")
    y_position += 20
    c.setFont("Helvetica", 12)
    c.drawString(40, height - y_position, "• Online: www.apspdcl.in")
    y_position += 20
    c.drawString(40, height - y_position, "• Mobile App: APSPDCL Mobile")
    y_position += 20
    c.drawString(40, height - y_position, "• In Person: Nearest APSPDCL Office")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(width/2 - 100, 50, "© 2025 Electricity Bill Calculator | All Rights Reserved")
    c.drawString(width/2 - 100, 30, "Please pay the bill in-time to avoid service interruption")
    
    # Save the PDF
    c.showPage()
    c.save()
    
    # Get the PDF value from the buffer
    buffer.seek(0)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="electricity_bill.pdf" class="download-btn">📄 Download Bill as PDF</a>'

def main():
    local_css()
    
    # App header
    st.markdown("<h1>⚡Andhra Pradesh Southern Power Distribution Company Limited💫</h1>", unsafe_allow_html=True)
    st.markdown("<h2>⚡APSPDCL⚡</h2>", unsafe_allow_html=True)

    
    # Initialize bill calculator
    bill_calculator = BillCalculator()
    
    # Download logo once at startup
    logo_path = download_and_save_logo()
    
    # Sidebar for navigation and info
    # with st.sidebar:
    #     if logo_path and os.path.exists(logo_path):
    #         try:
    #             st.image(logo_path, width=250)
    #         except:
    #             st.image("https://api.placeholder.com/400/320", width=250)
    #     else:
    #         st.image("https://api.placeholder.com/400/320", width=250)
        
    #     st.markdown("<h3>Navigation</h3>", unsafe_allow_html=True)
    #     page = st.radio("Navigation", ["Calculate Bill", "Tariff Information", "Bill History", "Help"], label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("<div class='info-box'>This calculator helps you estimate electricity bills for different customer types based on meter readings.</div>", unsafe_allow_html=True)
        
        # Show current date/time
        now = datetime.datetime.now()
        st.markdown(f"<p style='text-align: center; color: gray;'>Today: {now.strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
    
    if page == "Calculate Bill":
        # Main bill calculation page
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Customer information section
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2>Customer Information</h2>", unsafe_allow_html=True)
            
            customer_type = st.selectbox(
                "Customer Type",
                ["Domestic", "Commercial", "Industrial"],
                help="Select the appropriate customer type for accurate billing"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                service_id = st.text_input("Service ID", help="Enter your unique service identifier")
            with col_b:
                customer_name = st.text_input("Customer Name", help="Enter the name on the account")
            
            # Display info about the selected customer type
            if customer_type == "Domestic":
                st.markdown("""
                <div class='info-box'>
                <strong>Domestic Rate Structure:</strong><br>
                • First 100 units: ₹1.50 per unit<br>
                • Next 100 units: ₹3.00 per unit<br>
                • Above 200 units: ₹4.50 per unit
                </div>
                """, unsafe_allow_html=True)
            elif customer_type == "Commercial":
                st.markdown("""
                <div class='info-box'>
                <strong>Commercial Rate Structure:</strong><br>
                • Flat rate: ₹5.00 per unit
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='info-box'>
                <strong>Industrial Rate Structure:</strong><br>
                • Peak hour usage: ₹8.00 per unit<br>
                • Normal hour usage: ₹6.00 per unit
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Meter readings section
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2>Meter Readings & Bill Period</h2>", unsafe_allow_html=True)
            
            # Bill date selection
            bill_date = st.date_input(
                "Bill Date",
                datetime.datetime.now(),
                help="Select the bill generation date"
            ).strftime("%Y-%m-%d")
            
            col_c, col_d = st.columns(2)
            with col_c:
                current_reading = st.number_input(
                    "Current Reading (kWh)",
                    min_value=0.0,
                    step=0.1,
                    format="%.1f",
                    help="Enter the latest meter reading"
                )
            with col_d:
                previous_reading = st.number_input(
                    "Previous Reading (kWh)",
                    min_value=0.0,
                    step=0.1,
                    format="%.1f",
                    help="Enter the previous meter reading"
                )
            
            peak_hour_units = 0
            if customer_type == "Industrial":
                peak_hour_units = st.number_input(
                    "Peak Hour Units (kWh)",
                    min_value=0.0,
                    max_value=current_reading-previous_reading if current_reading > previous_reading else 0.0,
                    step=0.1,
                    format="%.1f",
                    help="Enter the number of units consumed during peak hours"
                )
            
            calculate_button = st.button("Calculate Bill", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Bill results section
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2>Bill Summary</h2>", unsafe_allow_html=True)
            
            if calculate_button:
                if not service_id or not customer_name:
                    st.error("Please enter Service ID and Customer Name")
                elif current_reading < previous_reading:
                    st.error("Current reading cannot be less than previous reading")
                else:
                    try:
                        # Calculate bill
                        result = bill_calculator.calculate_bill(
                            customer_type, 
                            current_reading, 
                            previous_reading,
                            bill_date,
                            peak_hour_units if customer_type == "Industrial" else 0
                        )
                        
                        st.success("Bill calculated successfully!")
                        
                        # Display metrics
                        col_result1, col_result2 = st.columns(2)
                        with col_result1:
                            st.metric("Units Consumed", f"{result['units_consumed']} kWh")
                            st.metric("Service Charge (5%)", f"₹{result['service_charge']}")
                            st.metric("Bill Date", f"{result['bill_date']}")
                        with col_result2:
                            st.metric("Net Bill", f"₹{result['net_bill']}")
                            st.metric("Total Bill", f"₹{result['total_bill']}")
                            st.metric("Due Date", f"{result['due_date']}")
                        
                        # Due date warning
                        today = datetime.datetime.now().date()
                        due_date = datetime.datetime.strptime(result['due_date'], "%Y-%m-%d").date()
                        days_remaining = (due_date - today).days
                        
                        if days_remaining < 0:
                            st.markdown(f"<div class='due-date-warning'>⚠️ Bill is past due by {abs(days_remaining)} days! Late payment charge of ₹{result['late_fee']} will be applied.</div>", unsafe_allow_html=True)
                        elif days_remaining <= 7:
                            st.markdown(f"<div class='due-date-warning'>⚠️ Due date approaching! {days_remaining} days remaining for payment.</div>", unsafe_allow_html=True)
                        
                        # Create bill data for download
                        bill_data = {
                            "Customer_Type": customer_type,
                            "Service_ID": service_id,
                            "Customer_Name": customer_name,
                            "Current_Reading": current_reading,
                            "Previous_Reading": previous_reading,
                            "Units_Consumed": result['units_consumed'],
                            "Net_Bill": result['net_bill'],
                            "Service_Charge": result['service_charge'],
                            "Total_Bill": result['total_bill'],
                            "Bill_Date": result['bill_date'],
                            "Due_Date": result['due_date'],
                            "Late_Fee": result['late_fee'],
                            "Amount_After_Due_Date": result['amount_after_due_date']
                        }
                        
                        if customer_type == "Industrial":
                            bill_data["Peak_Hour_Units"] = peak_hour_units
                        
                        # Payment info
                        st.markdown("<div class='payment-info'>", unsafe_allow_html=True)
                        st.markdown("<h3>Payment Information</h3>", unsafe_allow_html=True)
                        st.markdown(f"""
                        • <strong>Due Date:</strong> {result['due_date']}
                        • <strong>Late Payment Fee (2%):</strong> ₹{result['late_fee']}
                        • <strong>Amount After Due Date:</strong> ₹{result['amount_after_due_date']}
                        """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Bill breakdown chart
                        st.markdown("<h3>Bill Breakdown</h3>", unsafe_allow_html=True)
                        
                        # Create a more attractive donut chart with Plotly
                        fig = go.Figure(go.Pie(
                            labels=['Net Bill', 'Service Charge'],
                            values=[result['net_bill'], result['service_charge']],
                            hole=.4,
                            marker_colors=['#1f77b4', '#ff7f0e']
                        ))
                        fig.update_layout(
                            margin=dict(l=20, r=20, t=30, b=20),
                            height=300,
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=0),
                            annotations=[dict(text=f"₹{result['total_bill']}", x=0.5, y=0.5, font_size=20, showarrow=False)]
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Save bill history
                        if 'bill_history' not in st.session_state:
                            st.session_state.bill_history = []
                        
                        # Add current bill to history
                        bill_history_entry = {
                            "invoice_no": f"AP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "customer_name": customer_name,
                            "service_id": service_id,
                            "bill_date": result['bill_date'],
                            "due_date": result['due_date'],
                            "units_consumed": result['units_consumed'],
                            "total_amount": result['total_bill']
                        }
                        st.session_state.bill_history.append(bill_history_entry)
                        
                        # Bill preview (before download)
                        with st.expander("Preview Bill Before Download"):
                            st.markdown("<h3>Electricity Bill</h3>", unsafe_allow_html=True)
                            
                            # Display logo
                            if logo_path and os.path.exists(logo_path):
                                try:
                                    st.image(logo_path, width=150)
                                except:
                                    st.write("Logo preview not available")
                            
                            col_preview1, col_preview2 = st.columns(2)
                            
                            with col_preview1:
                                st.markdown("**Customer Information**")
                                st.write(f"Customer Name: {customer_name}")
                                st.write(f"Service ID: {service_id}")
                                st.write(f"Customer Type: {customer_type}")
                            
                            with col_preview2:
                                st.markdown("**Bill Details**")
                                st.write(f"Bill Date: {result['bill_date']}")
                                st.write(f"Due Date: {result['due_date']}")
                                st.write(f"Invoice #: AP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
                            
                            st.markdown("---")
                            
                            col_preview3, col_preview4 = st.columns(2)
                            
                            with col_preview3:
                                st.markdown("**Meter Readings**")
                                st.write(f"Previous Reading: {previous_reading} kWh")
                                st.write(f"Current Reading: {current_reading} kWh")
                                st.write(f"Units Consumed: {result['units_consumed']} kWh")
                                
                                if customer_type == "Industrial":
                                    st.write(f"Peak Hour Units: {peak_hour_units} kWh")
                            
                            with col_preview4:
                                st.markdown("**Bill Summary**")
                                st.write(f"Net Bill: ₹{result['net_bill']}")
                                st.write(f"Service Charge (5%): ₹{result['service_charge']}")
                                st.markdown(f"**Total Bill: ₹{result['total_bill']}**")
                                st.write(f"Late Payment Fee (2%): ₹{result['late_fee']}")
                                st.markdown(f"**Amount After Due Date: ₹{result['amount_after_due_date']}**")
                        
                        # Download options
                        st.markdown("<h3>Download Bill</h3>", unsafe_allow_html=True)
                        st.markdown(generate_pdf(bill_data), unsafe_allow_html=True)
                        
                    except ValueError as e:
                        st.error(str(e))
            else:
                # Placeholder content when no calculation has been done
                st.info("Enter customer information and meter readings, then click 'Calculate Bill' to see results.")
                
                # Sample chart as placeholder
                fig = go.Figure()
                fig.add_trace(go.Indicator(
                    mode = "gauge+number",
                    value = 0,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Total Bill (₹)"},
                    gauge = {
                        'axis': {'range': [None, 1000]},
                        'bar': {'color': "lightblue"},
                        'steps': [
                            {'range': [0, 250], 'color': "lightgreen"},
                            {'range': [250, 500], 'color': "yellow"},
                            {'range': [500, 1000], 'color': "orange"}
                        ]
                    }
                ))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    elif page == "Tariff Information":
        # Tariff information page
        st.markdown("<h2>Electricity Tariff Structure</h2>", unsafe_allow_html=True)
        
        # Create tabs for different customer types
        tab1, tab2, tab3 = st.tabs(["Domestic", "Commercial", "Industrial"])
        
        with tab1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Domestic Customer Rates</h3>", unsafe_allow_html=True)
            st.markdown("""
            - **First 100 units**: ₹1.50 per unit
            - **Next 100 units**: ₹3.00 per unit
            - **Above 200 units**: ₹4.50 per unit
            """)
            
            # Visual representation of tier pricing
            tiers = ['Tier 1 (0-100 kWh)', 'Tier 2 (101-200 kWh)', 'Tier 3 (>200 kWh)']
            rates = [1.50, 3.00, 4.50]
            
            fig = px.bar(
                x=tiers, y=rates,
                labels={'x': 'Consumption Tier', 'y': 'Rate (₹ per kWh)'},
                text=[f"₹{r:.2f}" for r in rates],
                color=rates,
                color_continuous_scale='blues'
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Commercial Customer Rates</h3>", unsafe_allow_html=True)
            st.markdown("""
            - **Flat rate**: ₹5.00 per unit
            -applies to all businesses, offices, and commercial properties""")
            # Commercial fixed rate visualization
            fig = px.bar(
                x=['Commercial Rate'], y=[5.0],
                labels={'x': 'Rate Type', 'y': 'Rate (₹ per kWh)'},
                text=["₹5.00"],
                color=[5.0],
                color_continuous_scale='oranges'
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Note**: Commercial customers are billed at a fixed rate regardless of consumption level.
            A 5% service charge is applied to all bills.
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Industrial Customer Rates</h3>", unsafe_allow_html=True)
            st.markdown("""
            - **Peak hour usage**: ₹8.00 per unit
            - **Normal hour usage**: ₹6.00 per unit
            """)
            
            # Industrial rate visualization
            rate_types = ['Normal Hours', 'Peak Hours']
            ind_rates = [6.00, 8.00]
            
            fig = px.bar(
                x=rate_types, y=ind_rates,
                labels={'x': 'Time Period', 'y': 'Rate (₹ per kWh)'},
                text=[f"₹{r:.2f}" for r in ind_rates],
                color=ind_rates,
                color_continuous_scale='reds'
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Note**: Industrial customers are charged based on time-of-use rates.
            A 5% service charge is applied to all bills.
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Additional info about bill calculation
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Additional Charges</h3>", unsafe_allow_html=True)
        st.markdown("""
        - **Service Charge**: 5% of the net bill amount
        - **Late Payment Fee**: 2% of the total bill amount (net bill + service charge)
        - **Due Date**: 15 days from bill generation date
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif page == "Bill History":
        # Bill history page
        st.markdown("<h2>Bill History</h2>", unsafe_allow_html=True)
        
        if 'bill_history' not in st.session_state or not st.session_state.bill_history:
            st.info("No bill history available. Generate a bill first.")
        else:
            st.markdown("<div class='bill-history'>", unsafe_allow_html=True)
            history_df = pd.DataFrame(st.session_state.bill_history)
            
            # Display bill history table
            st.dataframe(
                history_df,
                column_config={
                    "invoice_no": "Invoice Number",
                    "customer_name": "Customer Name",
                    "service_id": "Service ID",
                    "bill_date": "Bill Date",
                    "due_date": "Due Date",
                    "units_consumed": "Units Consumed",
                    "total_amount": "Total Amount (₹)"
                },
                use_container_width=True
            )
            
            # Add visualization of bill history
            st.markdown("<h3>Bill History Trends</h3>", unsafe_allow_html=True)
            
            # Convert bill date to datetime
            history_df['bill_date'] = pd.to_datetime(history_df['bill_date'])
            
            # Line chart for consumption
            fig1 = px.line(
                history_df.sort_values('bill_date'), 
                x='bill_date', 
                y='units_consumed',
                markers=True,
                labels={'bill_date': 'Billing Date', 'units_consumed': 'Units Consumed (kWh)'},
                title='Consumption Trend'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Line chart for bill amount
            fig2 = px.line(
                history_df.sort_values('bill_date'), 
                x='bill_date', 
                y='total_amount',
                markers=True,
                labels={'bill_date': 'Billing Date', 'total_amount': 'Total Bill Amount (₹)'},
                title='Bill Amount Trend'
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Option to clear history
            if st.button("Clear Bill History"):
                st.session_state.bill_history = []
                st.success("Bill history cleared successfully!")
                st.rerun()
    
    elif page == "Help":
        # Help page
        st.markdown("<h2>Help & FAQs</h2>", unsafe_allow_html=True)
        
        # FAQ sections
        with st.expander("How is my electricity bill calculated?"):
            st.markdown("""
            Your electricity bill is calculated based on:
            
            1. **Customer Type**: Different rates apply for Domestic, Commercial, and Industrial customers
            2. **Units Consumed**: The difference between your current and previous meter readings
            3. **Applicable Rates**: 
               - Domestic: Tiered pricing (1.50/3.00/4.50 Rs per unit)
               - Commercial: Flat rate (5.00 Rs per unit)
               - Industrial: Time-of-use rates (6.00 Rs normal hours, 8.00 Rs peak hours)
            4. **Service Charge**: 5% of the net bill amount
            5. **Late Payment Fee**: 2% if paid after the due date
            """)
        
        with st.expander("What is the due date for payment?"):
            st.markdown("""
            The due date is automatically calculated as 15 days from the bill generation date.
            If payment is not received by the due date, a 2% late payment fee will be applied to the total bill amount.
            """)
        
        with st.expander("How can I download my bill?"):
            st.markdown("""
            After calculating your bill:
            1. Click the "Preview Bill" expander to review your bill details
            2. Click the "Download Bill as PDF" button to download a copy of your bill
            """)
        
        with st.expander("What is peak hour usage for Industrial customers?"):
            st.markdown("""
            Peak hours are typically periods of highest electricity demand, usually between 6 PM and 10 PM.
            Industrial customers are charged a higher rate (8.00 Rs per unit) for electricity consumed during these hours.
            """)
        
        with st.expander("Contact Information"):
            st.markdown("""
            **APSPDCL Customer Service**
            - Customer Care: 1912
            - Email: info@apspdcl.in
            - Website: www.apspdcl.in
            
            **Head Office**
            - APSPDCL, Corporate Office
            - Tiruchanoor Road, Tirupati
            - Andhra Pradesh - 517503
            """)
            
        # Tutorial section
        st.markdown("<h3>How to Use This Application</h3>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("""
        **Step 1**: Select "Calculate Bill" from the sidebar navigation
        
        **Step 2**: Enter customer information:
        - Select customer type (Domestic, Commercial, or Industrial)
        - Enter Service ID and Customer Name
        
        **Step 3**: Enter meter readings:
        - Enter bill date
        - Enter current and previous meter readings
        - For Industrial customers, enter peak hour units
        
        **Step 4**: Click "Calculate Bill" button
        
        **Step 5**: Review bill summary and download as needed
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # About section
        st.markdown("<h3>About This Application</h3>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("""
        This Electricity Bill Calculator is developed for APSPDCL to help customers estimate their electricity bills based on their consumption patterns. The application provides:
        
        - Accurate bill calculation based on current tariff structures
        - Bill history tracking for consumption analysis
        - PDF bill generation for record keeping
        - Visualization of consumption patterns
        
        **Version**: 1.0
        **Last Updated**: April 2025
        """)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
