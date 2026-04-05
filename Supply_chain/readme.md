# 💊 Drug Expiry & Inventory Dashboard

A pharmacy inventory management dashboard that flags expiring drugs, quantifies stock value at risk, and gives supply chain teams a clear picture of what needs action — and when.

Built with Python, Pandas, Plotly, and Streamlit.

---

## The Problem

Expired drugs are a silent drain on pharmacy operations. Stock sits on shelves past its expiry date, value is written off, and in worse cases — compromised medicine reaches patients. Most pharmacies track inventory in scattered Excel sheets with no early warning system.

This dashboard solves that.

---

## What It Does

- **Flags every batch** as Expired, Critical (≤30 days), Warning (31–90 days), or Safe
- **Calculates ₦ value at risk** — expired and critical stock combined
- **Shows where the risk lives** — by location, drug category, and individual product
- **Visualizes monthly expiry** — units expiring over the next 6 months
- **Searchable inventory table** — filterable by location, category, and status

---

## Dashboard Preview

| Section | What It Shows |
|---|---|
| KPI Cards | Value at risk, expired count, critical count, warning count, total SKUs |
| Expiry Bar Chart | Units expiring month by month for the next 6 months |
| Status Donut | Proportion of stock in each status category |
| Risk by Location | Which branch carries the most at-risk value |
| Top Drugs at Risk | Highest ₦ exposure by individual drug |
| Category Heatmap | Full inventory value broken down by category and status |
| Inventory Table | Searchable, color-coded, sortable detail view |

---

## Project Structure

```
drug-expiry-dashboard/
├── dashboard.py                      # Main Streamlit app && # Data cleaning & analysis script
├── pharmacy_inventory.xlsx           # Source inventory data
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## Quickstart

### 1. Clone the repository

```bash
git clone "https://github.com/baylon-obinna/HealthTech-Projects.git"
cd Supply_chain
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the analysis script

This reads the Excel file and produces a clean CSV for the dashboard:

You should see a summary report printed in your terminal — total SKUs, value at risk, top drugs, risk by location.

### 4. Launch the dashboard

```bash
python -m streamlit run dashboard.py
```

Opens automatically at `http://localhost:8501`

---

## Using Your Own Pharmacy Data

You can replace the sample data with real inventory data from your pharmacy in three steps.

### Step 1 — Prepare your Excel file

Your file needs these columns. Column names must match exactly:

| Column | Description | Example |
|---|---|---|
| `drug_name` | Full drug name and strength | Amoxicillin 500mg |
| `category` | Therapeutic category | Antibiotic |
| `dosage_form` | Tablet, Capsule, Syrup, etc. | Capsule |
| `batch_number` | Unique batch identifier | BN1033 |
| `quantity` | Units in stock | 218 |
| `unit_cost_ngn` | Cost per unit in Naira | 4153.67 |
| `total_value_ngn` | quantity × unit cost | 905500.06 |
| `date_received` | Date stock arrived | 2025-11-11 |
| `expiry_date` | Manufacturer expiry date | 2026-10-27 |
| `supplier` | Supplier or distributor name | May & Baker Nigeria |
| `location` | Branch or store name | Lagos Main Store |

Dates should be in `YYYY-MM-DD` format. If your dates are in another format (e.g. `27/10/2026`), open the file in Excel, select the date columns, and format them as `YYYY-MM-DD` before saving.

### Step 2 — Replace the data file

Save your file as `pharmacy_inventory.xlsx` in the project folder, replacing the existing sample file.

### Step 3 — Run and view

```bash
python -m streamlit run dashboard.py
```

The dashboard will now reflect your real inventory data.

---

## Deploy Online

To get a shareable link you can send to anyone:

### 1. Push to GitHub

Upload all project files to a public GitHub repository.

### 2. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **Create app**
4. Select your repository, set branch to `main`, set main file to `dashboard.py`
5. Click **Deploy**

Your live URL will look like:
```
https://your-username-drug-expiry-dashboard.streamlit.app
```

No login required to view the dashboard. Free to host.

---

## Requirements

```
streamlit
pandas
plotly
openpyxl
```

Python 3.8 or above.

---

## Status Definitions

| Status | Condition | Recommended Action |
|---|---|---|
| 🔴 Expired | Expiry date has passed | Quarantine immediately, initiate return or disposal |
| 🟠 Critical | Expires within 30 days | Prioritize dispensing, contact supplier for credit |
| 🟡 Warning | Expires in 31–90 days | Monitor closely, consider promotions or transfers |
| 🟢 Safe | More than 90 days remaining | No immediate action required |

---

## Built With

- [Python](https://python.org) — core language
- [Pandas](https://pandas.pydata.org) — data cleaning and analysis
- [Plotly](https://plotly.com/python) — interactive charts
- [Streamlit](https://streamlit.io) — dashboard framework and deployment

---

## Author

Built as part of a pharma data portfolio focused on supply chain intelligence for the Nigerian healthcare market.