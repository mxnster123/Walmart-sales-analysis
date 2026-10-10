import pandas as pd


# Load Walmart sales dataset
df = pd.read_csv("Walmart_Sales.csv")

# Convert Date column to datetime format
df["Date"] = pd.to_datetime(
    df["Date"],
    dayfirst=True,
    errors="coerce"
)

# Overall business performance
total_sales = df["Weekly_Sales"].sum()

# STEP 1: Business Performance Analysis

total_sales = df["Weekly_Sales"].sum()
average_sales = df["Weekly_Sales"].mean()
total_stores = df["Store"].nunique()

store_sales = (
    df.groupby("Store")["Weekly_Sales"]
    .sum()
    .sort_values(ascending=False)
)

top_store = store_sales.idxmax()
top_store_sales = store_sales.max()

bottom_store = store_sales.idxmin()
bottom_store_sales = store_sales.min()

top_store_share = (top_store_sales / total_sales) * 100

print("\n===== BUSINESS PERFORMANCE ANALYSIS =====")
print(f"Total Sales: ${total_sales:,.2f}")
print(f"Average Sales per Record: ${average_sales:,.2f}")
print(f"Total Stores: {total_stores}")

print(f"\nTop Store: {top_store}")
print(f"Top Store Sales: ${top_store_sales:,.2f}")

print(f"\nLowest-Sales Store: {bottom_store}")
print(f"Lowest-Sales Store Sales: ${bottom_store_sales:,.2f}")

print(f"\nTop Store Share of Total Sales: {top_store_share:.2f}%")


# STEP 2: Sales Contribution Analysis

store_sales = (
    df.groupby("Store")["Weekly_Sales"]
    .sum()
    .sort_values(ascending=False)
)

total_sales = df["Weekly_Sales"].sum()

top_5_sales = store_sales.head(5).sum()
top_10_sales = store_sales.head(10).sum()

top_5_share = (top_5_sales / total_sales) * 100
top_10_share = (top_10_sales / total_sales) * 100

print("\n===== SALES CONTRIBUTION ANALYSIS =====")

print(f"Top 5 Stores Sales: ${top_5_sales:,.2f}")
print(f"Top 5 Stores Contribution: {top_5_share:.2f}%")

print(f"\nTop 10 Stores Sales: ${top_10_sales:,.2f}")
print(f"Top 10 Stores Contribution: {top_10_share:.2f}%")

print(f"\nRemaining 35 Stores Contribution: "
      f"{100 - top_10_share:.2f}%")


# STEP 3: Monthly Sales Trend Analysis

df["Month"] = df["Date"].dt.to_period("M").astype(str)

monthly_analysis = df.groupby("Month").agg(
    Total_Recorded_Sales=("Weekly_Sales", "sum"),
    Average_Weekly_Sales=("Weekly_Sales", "mean"),
    Number_of_Records=("Weekly_Sales", "count")
).reset_index()

# Rank months by average weekly sales
monthly_rank = monthly_analysis.sort_values(
    "Average_Weekly_Sales", ascending=False
)

best_month = monthly_rank.iloc[0]
lowest_month = monthly_rank.iloc[-1]

print("\n===== MONTHLY SALES ANALYSIS =====")

print("\nTop 5 Months by Average Weekly Sales:")
print(
    monthly_rank[
        ["Month", "Average_Weekly_Sales", "Number_of_Records"]
    ].head(5).to_string(index=False)
)

print("\nLowest 5 Months by Average Weekly Sales:")
print(
    monthly_rank[
        ["Month", "Average_Weekly_Sales", "Number_of_Records"]
    ].tail(5).to_string(index=False)
)

print(f"\nHighest Average Sales Month: {best_month['Month']}")
print(
    f"Average Weekly Sales: "
    f"${best_month['Average_Weekly_Sales']:,.2f}"
)

print(f"\nLowest Average Sales Month: {lowest_month['Month']}")
print(
    f"Average Weekly Sales: "
    f"${lowest_month['Average_Weekly_Sales']:,.2f}"
)

# STEP 4: Holiday vs Non-Holiday Sales Analysis

holiday_analysis = df.groupby("Holiday_Flag").agg(
    Average_Weekly_Sales=("Weekly_Sales", "mean"),
    Total_Recorded_Sales=("Weekly_Sales", "sum"),
    Number_of_Records=("Weekly_Sales", "count")
).reset_index()

print("\n===== HOLIDAY VS NON-HOLIDAY ANALYSIS =====")

print("\n0 = Non-Holiday, 1 = Holiday")
print(holiday_analysis.to_string(index=False))

# Compare average weekly sales
non_holiday_sales = holiday_analysis.loc[
    holiday_analysis["Holiday_Flag"] == 0,
    "Average_Weekly_Sales"
].iloc[0]

holiday_sales = holiday_analysis.loc[
    holiday_analysis["Holiday_Flag"] == 1,
    "Average_Weekly_Sales"
].iloc[0]

difference = holiday_sales - non_holiday_sales
percentage_difference = (difference / non_holiday_sales) * 100

print(f"\nNon-Holiday Average Sales: ${non_holiday_sales:,.2f}")
print(f"Holiday Average Sales: ${holiday_sales:,.2f}")
print(f"Difference: ${difference:,.2f}")
print(f"Percentage Difference: {percentage_difference:.2f}%")

# STEP 4: Holiday vs Non-Holiday Sales Analysis

holiday_analysis = df.groupby("Holiday_Flag").agg(
    Average_Weekly_Sales=("Weekly_Sales", "mean"),
    Total_Recorded_Sales=("Weekly_Sales", "sum"),
    Number_of_Records=("Weekly_Sales", "count")
).reset_index()

print("\n===== HOLIDAY VS NON-HOLIDAY ANALYSIS =====")

print("\n0 = Non-Holiday, 1 = Holiday")
print(holiday_analysis.to_string(index=False))

# Compare average weekly sales
non_holiday_sales = holiday_analysis.loc[
    holiday_analysis["Holiday_Flag"] == 0,
    "Average_Weekly_Sales"
].iloc[0]

holiday_sales = holiday_analysis.loc[
    holiday_analysis["Holiday_Flag"] == 1,
    "Average_Weekly_Sales"
].iloc[0]

difference = holiday_sales - non_holiday_sales
percentage_difference = (difference / non_holiday_sales) * 100

print(f"\nNon-Holiday Average Sales: ${non_holiday_sales:,.2f}")
print(f"Holiday Average Sales: ${holiday_sales:,.2f}")
print(f"Difference: ${difference:,.2f}")
print(f"Percentage Difference: {percentage_difference:.2f}%")

# STEP 6: Economic Factors Analysis

economic_factors = [
    "Temperature",
    "Fuel_Price",
    "CPI",
    "Unemployment"
]

print("\n===== ECONOMIC FACTORS ANALYSIS =====")

for factor in economic_factors:

    correlation = df["Weekly_Sales"].corr(df[factor])

    print(f"{factor} vs Weekly Sales Correlation: {correlation:.3f}")

    if correlation > 0:
        print("Relationship: Positive")
    elif correlation < 0:
        print("Relationship: Negative")
    else:
        print("Relationship: No linear correlation")

    print("-" * 40)

    # STEP 7: Weekly Sales Stability Analysis

weekly_analysis = df.groupby("Date").agg(
    Total_Weekly_Sales=("Weekly_Sales", "sum")
).reset_index()

average_sales = weekly_analysis["Total_Weekly_Sales"].mean()
highest_sales = weekly_analysis["Total_Weekly_Sales"].max()
lowest_sales = weekly_analysis["Total_Weekly_Sales"].min()
sales_std = weekly_analysis["Total_Weekly_Sales"].std()

highest_date = weekly_analysis.loc[
    weekly_analysis["Total_Weekly_Sales"].idxmax(), "Date"
]

lowest_date = weekly_analysis.loc[
    weekly_analysis["Total_Weekly_Sales"].idxmin(), "Date"
]

print("\n===== WEEKLY SALES STABILITY ANALYSIS =====")

print(f"Average Total Weekly Sales: ${average_sales:,.2f}")
print(f"Highest Total Weekly Sales: ${highest_sales:,.2f}")
print(f"Highest Sales Date: {highest_date.date()}")

print(f"Lowest Total Weekly Sales: ${lowest_sales:,.2f}")
print(f"Lowest Sales Date: {lowest_date.date()}")

print(f"Standard Deviation: ${sales_std:,.2f}")

# Measure variation relative to average sales
coefficient_variation = (sales_std / average_sales) * 100

print(f"Sales Variation: {coefficient_variation:.2f}%")

# STEP 9: Yearly Sales Analysis

df["Year"] = df["Date"].dt.year

yearly_analysis = df.groupby("Year").agg(
    Total_Sales=("Weekly_Sales", "sum"),
    Average_Weekly_Sales=("Weekly_Sales", "mean"),
    Number_of_Records=("Weekly_Sales", "count")
).reset_index()

print("\n===== YEARLY SALES ANALYSIS =====")

print(yearly_analysis.round(2).to_string(index=False))

# Compare consecutive years
yearly_analysis = yearly_analysis.sort_values("Year")

yearly_analysis["Sales_Growth_Percentage"] = (
    yearly_analysis["Total_Sales"].pct_change() * 100
)

print("\n===== YEARLY SALES GROWTH =====")

print(
    yearly_analysis[
        ["Year", "Total_Sales", "Sales_Growth_Percentage"]
    ].round(2).to_string(index=False)
)

# STEP 10: Business Summary

print("\n" + "=" * 50)
print("       WALMART SALES BUSINESS SUMMARY")
print("=" * 50)

print(f"\n1. Total Recorded Sales: ${df['Weekly_Sales'].sum():,.2f}")

print(f"\n2. Average Weekly Sales per Record: ${df['Weekly_Sales'].mean():,.2f}")

# Best store by total recorded sales
store_sales = df.groupby("Store")["Weekly_Sales"].sum()

best_store = store_sales.idxmax()
lowest_store = store_sales.idxmin()

print(f"\n3. Highest Sales Store: Store {best_store}")
print(f"   Total Sales: ${store_sales.max():,.2f}")

print(f"\n4. Lowest Sales Store: Store {lowest_store}")
print(f"   Total Sales: ${store_sales.min():,.2f}")

# Holiday comparison
holiday_means = df.groupby("Holiday_Flag")["Weekly_Sales"].mean()

print(f"\n5. Average Non-Holiday Sales: ${holiday_means.loc[0]:,.2f}")
print(f"6. Average Holiday Sales: ${holiday_means.loc[1]:,.2f}")

# Monthly average sales
df["Month"] = df["Date"].dt.to_period("M")

monthly_sales = df.groupby("Month")["Weekly_Sales"].mean()

print(f"\n7. Highest Average-Sales Month: {monthly_sales.idxmax()}")
print(f"   Average Sales: ${monthly_sales.max():,.2f}")

print(f"\n8. Lowest Average-Sales Month: {monthly_sales.idxmin()}")
print(f"   Average Sales: ${monthly_sales.min():,.2f}")

print("\n" + "=" * 50)
print("           END OF BUSINESS SUMMARY")
print("=" * 50)

