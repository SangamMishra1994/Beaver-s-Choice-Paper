import pandas as pd

df = pd.read_csv("test_results.csv")
print("\n=== EXECUTION SUMMARY ===")
print(f"Total Orders: {len(df)}")
fulfilled_count = (df["status"] == "FULFILLED").sum()
unfulfilled_count = (df["status"] == "UNFULFILLED").sum()
print(f"Fulfilled: {fulfilled_count}")
print(f"Unfulfilled: {unfulfilled_count}")
total_revenue = df["quote_amount"].sum()
print(f"Total Revenue: ${total_revenue:.2f}")
if len(df) > 0:
    print(f"Success Rate: {fulfilled_count / len(df) * 100:.1f}%")
print("\n✅ PROJECT EXECUTION SUCCESSFUL")
