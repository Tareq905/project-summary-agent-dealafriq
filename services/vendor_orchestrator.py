from fetchers.vendor_fetcher import fetch_all_vendor_data, fetch_pm_context
from agents.vendor_agent import run_vendor_analysis

def analyze_all_vendors():
    vendors = fetch_all_vendor_data()
    pms = fetch_pm_context()
    
    report = []
    for vendor in vendors:
        # Pass the vendor object and PM list for full context
        result = run_vendor_analysis(vendor, pms)
        report.append(result)
        
    return report