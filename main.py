import os
import csv
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# Define state structure
class CarbonState(TypedDict):
    csv_path: str
    raw_records: List[Dict[str, str]]
    classified_records: List[Dict[str, Any]]
    scope_totals: Dict[str, float]
    total_emissions: float
    report_path: str
    current_step: str

# Emission Factors (Metric Tons CO2e per unit)
EMISSION_FACTORS = {
    "scope_1_diesel": 0.0101,  
    "scope_2_electricity": 0.00017, 
    "scope_3_flights": 0.68     
}

# 1. Data Normalizer Node
def data_normalizer_node(state: CarbonState) -> Dict[str, Any]:
    print("--- [Node: Data Normalizer] ---")
    path = state["csv_path"]
    records = []
    
    if os.path.exists(path):
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
    else:
        records = [
            {"TRANSACTION_ID": "TX-00918", "DESCRIPTION": "Grid Power usage", "QTY": "12500 kWh"},
            {"TRANSACTION_ID": "TX-00922", "DESCRIPTION": "Flights (London-NY)", "QTY": "3 tickets"},
            {"TRANSACTION_ID": "TX-00945", "DESCRIPTION": "Diesel freight", "QTY": "420 gallons"}
        ]
        
    return {
        "raw_records": records,
        "current_step": "DATA_NORMALIZED"
    }

# 2. Scope Classifier Node
def scope_classifier_node(state: CarbonState) -> Dict[str, Any]:
    print("--- [Node: Scope Classifier] ---")
    raw = state["raw_records"]
    classified = []
    
    for rec in raw:
        desc = rec["DESCRIPTION"].lower()
        qty_str = rec["QTY"]
        qty_val = float(qty_str.split(" ")[0])
        unit = qty_str.split(" ")[1] if len(qty_str.split(" ")) > 1 else ""
        
        scope = "Scope 3"
        factor_key = "scope_3_flights"
        
        if "diesel" in desc or "fuel" in desc:
            scope = "Scope 1"
            factor_key = "scope_1_diesel"
        elif "grid" in desc or "electricity" in desc or "power" in desc:
            scope = "Scope 2"
            factor_key = "scope_2_electricity"
            
        classified.append({
            "id": rec.get("TRANSACTION_ID", "N/A"),
            "date": rec.get("DATE", "N/A"),
            "desc": rec["DESCRIPTION"],
            "qty": qty_val,
            "unit": unit,
            "scope": scope,
            "factor_key": factor_key
        })
        
    return {
        "classified_records": classified,
        "current_step": "SCOPE_CLASSIFIED"
    }

# 3. Carbon Calculator & Exporter Node
def carbon_calculator_exporter_node(state: CarbonState) -> Dict[str, Any]:
    print("--- [Node: Carbon Calculator & Exporter] ---")
    classified = state["classified_records"]
    totals = {"Scope 1": 0.0, "Scope 2": 0.0, "Scope 3": 0.0}
    net_sum = 0.0
    
    for item in classified:
        factor = EMISSION_FACTORS.get(item["factor_key"], 0.0)
        co2e = item["qty"] * factor
        item["co2e_mt"] = co2e
        totals[item["scope"]] += co2e
        net_sum += co2e
        
    # Generate styled ESG HTML Report
    scope1_pct = (totals["Scope 1"] / net_sum * 100) if net_sum > 0 else 0
    scope2_pct = (totals["Scope 2"] / net_sum * 100) if net_sum > 0 else 0
    scope3_pct = (totals["Scope 3"] / net_sum * 100) if net_sum > 0 else 0
    
    radius = 60
    circ = 2 * 3.14159 * radius
    pct = Math_min = (net_sum / 20) * 100
    offset = circ - (min(pct, 100) / 100) * circ
    
    table_rows = ""
    for item in classified:
        table_rows += f"""
        <tr>
          <td>{item['id']}</td>
          <td>{item['date']}</td>
          <td>{item['desc']}</td>
          <td>{item['scope']}</td>
          <td>{item['qty']} {item['unit']}</td>
          <td style="font-weight:600; color:#fff;">{item['co2e_mt']:.2f} MT</td>
        </tr>
        """
        
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vanguard ESG Compliance Dashboard</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    :root {{
      --bg-dark: #07090e;
      --bg-card: #10141d;
      --border: rgba(255, 255, 255, 0.05);
      --text-main: #f1f5f9;
      --text-muted: #64748b;
      --accent-green: #6fbf4a;
      --scope1: #ef4444;
      --scope2: #eab308;
      --scope3: #3b82f6;
    }}
    
    body {{
      background: var(--bg-dark);
      color: var(--text-main);
      font-family: 'Outfit', sans-serif;
      margin: 0;
      padding: 40px 24px;
    }}
    
    .dashboard-container {{
      max-width: 1100px;
      margin: 0 auto;
    }}
    
    header {{
      margin-bottom: 40px;
    }}
    
    header h1 {{
      font-size: 2.2rem;
      font-weight: 700;
      margin: 0 0 8px 0;
      letter-spacing: -0.02em;
    }}
    
    .subtitle {{
      color: var(--text-muted);
      font-size: 1rem;
    }}
    
    .grid-top {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 32px;
      margin-bottom: 40px;
    }}
    
    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 32px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    
    .card-title {{
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 24px;
    }}
    
    .radial-progress {{
      position: relative;
      width: 150px;
      height: 150px;
    }}
    
    .radial-svg {{
      transform: rotate(-90deg);
    }}
    
    .radial-bg {{
      fill: none;
      stroke: rgba(255, 255, 255, 0.03);
      stroke-width: 12;
    }}
    
    .radial-bar {{
      fill: none;
      stroke: var(--accent-green);
      stroke-width: 12;
      stroke-linecap: round;
      stroke-dasharray: {circ:.1f};
      stroke-dashoffset: {offset:.1f};
    }}
    
    .radial-text {{
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }}
    
    .radial-val {{
      font-size: 2.2rem;
      font-weight: 700;
      color: #fff;
    }}
    
    .radial-lbl {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }}
    
    .scope-list {{
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    
    .scope-row {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    
    .scope-meta {{
      display: flex;
      justify-content: space-between;
      font-size: 0.9rem;
    }}
    
    .scope-name {{ font-weight: 500; }}
    .scope-val {{ color: var(--text-muted); }}
    
    .scope-track {{
      height: 10px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 5px;
      overflow: hidden;
    }}
    
    .scope-bar {{
      height: 100%;
      border-radius: 5px;
    }}
    
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
    }}
    
    th, td {{
      padding: 16px 24px;
      text-align: left;
      border-bottom: 1px solid var(--border);
      font-size: 0.9rem;
    }}
    
    th {{
      background: rgba(255, 255, 255, 0.01);
      font-weight: 600;
      color: var(--text-muted);
    }}
  </style>
</head>
<body>
  <div class="dashboard-container">
    <header>
      <h1>Vanguard ESG Compliance Dashboard</h1>
      <div class="subtitle">Scope 1/2/3 Greenhouse Gas Audit</div>
    </header>
    
    <div class="grid-top">
      <div class="card">
        <div class="card-title">Cumulative Carbon Footprint</div>
        <div class="radial-progress">
          <svg width="150" height="150" class="radial-svg">
            <circle cx="75" cy="75" r="{radius}" class="radial-bg"></circle>
            <circle cx="75" cy="75" r="{radius}" class="radial-bar"></circle>
          </svg>
          <div class="radial-text">
            <span class="radial-val">{net_sum:.2f}</span>
            <span class="radial-lbl">MT CO2e</span>
          </div>
        </div>
      </div>
      
      <div class="card" style="align-items:stretch;">
        <div class="card-title" style="text-align:center;">Emissions Breakdown</div>
        <div class="scope-list">
          <div class="scope-row">
            <div class="scope-meta">
              <span class="scope-name">Scope 1 (Direct Combustion)</span>
              <span class="scope-val">{totals['Scope 1']:.2f} MT ({scope1_pct:.0f}%)</span>
            </div>
            <div class="scope-track">
              <div class="scope-bar" style="width:{scope1_pct}%; background:var(--scope1);"></div>
            </div>
          </div>
          
          <div class="scope-row">
            <div class="scope-meta">
              <span class="scope-name">Scope 2 (Electricity)</span>
              <span class="scope-val">{totals['Scope 2']:.2f} MT ({scope2_pct:.0f}%)</span>
            </div>
            <div class="scope-track">
              <div class="scope-bar" style="width:{scope2_pct}%; background:var(--scope2);"></div>
            </div>
          </div>
          
          <div class="scope-row">
            <div class="scope-meta">
              <span class="scope-name">Scope 3 (Business Travel)</span>
              <span class="scope-val">{totals['Scope 3']:.2f} MT ({scope3_pct:.0f}%)</span>
            </div>
            <div class="scope-track">
              <div class="scope-bar" style="width:{scope3_pct}%; background:var(--scope3);"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <h2>Audited Ledger Logs</h2>
    <table>
      <thead>
        <tr>
          <th>Transaction ID</th>
          <th>Date</th>
          <th>Description</th>
          <th>GHG Category</th>
          <th>Ledger Qty</th>
          <th>Emissions (CO2e)</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>
</body>
</html>
    """
    
    report_file = os.path.join(os.path.dirname(__file__), "esg_report.html")
    with open(report_file, "w") as f:
        f.write(html_content)
        
    return {
        "classified_records": classified,
        "scope_totals": totals,
        "total_emissions": net_sum,
        "report_path": report_file,
        "current_step": "REPORT_EXPORTED"
    }

# Build workflow
def build_esg_compliance_workflow():
    workflow = StateGraph(CarbonState)
    
    workflow.add_node("normalize_data", data_normalizer_node)
    workflow.add_node("classify_scope", scope_classifier_node)
    workflow.add_node("calculate_carbon", carbon_calculator_node)
    
    workflow.set_entry_point("normalize_data")
    workflow.add_edge("normalize_data", "classify_scope")
    workflow.add_edge("classify_scope", "calculate_carbon")
    workflow.add_edge("calculate_carbon", END)
    
    return workflow.compile()

if __name__ == "__main__":
    print("====================================================")
    print("  Vanguard Compliance Engine (Elevated)             ")
    print("====================================================")
    
    csv_file = os.path.join(os.path.dirname(__file__), "sample_erp_data.csv")
    initial_state = {
        "csv_path": csv_file,
        "raw_records": [],
        "classified_records": [],
        "scope_totals": {},
        "total_emissions": 0.0,
        "report_path": "",
        "current_step": "INIT"
    }
    
    # Run
    workflow = StateGraph(CarbonState)
    workflow.add_node("normalize_data", data_normalizer_node)
    workflow.add_node("classify_scope", scope_classifier_node)
    workflow.add_node("calculate_carbon", carbon_calculator_exporter_node) # Elevated node
    workflow.set_entry_point("normalize_data")
    workflow.add_edge("normalize_data", "classify_scope")
    workflow.add_edge("classify_scope", "calculate_carbon")
    workflow.add_edge("calculate_carbon", END)
    
    app = workflow.compile()
    res = app.invoke(initial_state)
    
    print("\n====================================================")
    print("  Vanguard Execution Completed                      ")
    print("====================================================")
    print(f"Compliance report exported successfully to:")
    print(f"  {res['report_path']}")
    print("====================================================\n")
