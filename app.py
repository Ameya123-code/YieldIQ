import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import altair as alt

st.set_page_config(page_title="YieldSense", layout="wide", initial_sidebar_state="collapsed")

# Load data
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "crop_production.csv")

css = """
<style>
body {
    background-color: #f5f5f5;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.header {
    background-color: #2E7D32;
    color: white;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 8px;
    margin-bottom: 20px;
}
.header h1 {
    margin: 0;
}
.search {
    padding: 5px;
    border: none;
    border-radius: 4px;
}
.export-btn {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}
.card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 20px;
    margin: 10px;
    text-align: center;
}
.card h3 {
    margin: 0;
    color: #2E7D32;
}
.card .value {
    font-size: 2em;
    font-weight: bold;
    color: #333;
}
.card .subtitle {
    color: #666;
    font-size: 0.9em;
}
.insights {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 20px;
    margin: 10px 0;
}
.insights h4 {
    color: #2E7D32;
}
</style>
"""

def preprocess_data(df):
    if "State_Name" in df.columns or "Crop_Year" in df.columns:
        df = df.rename(columns={
            "State_Name": "State",
            "District_Name": "District",
            "Crop_Year": "Year",
            "Area": "Area",
            "Production": "Production",
            "Season": "Season",
            "Crop": "Crop"
        })

    df = df.rename(columns={
        "State": "State",
        "District": "District",
        "Crop": "Crop",
        "Season": "Season",
        "Year": "Year",
        "Area": "Area",
        "Production": "Production"
    })

    df = df.dropna(subset=["State", "Crop", "Season", "Area", "Production", "Year"])

    for col in ["State", "District", "Crop", "Season"]:
        df[col] = df[col].astype(str).str.strip().str.title()

    df["Area"] = pd.to_numeric(df["Area"], errors="coerce")
    df["Production"] = pd.to_numeric(df["Production"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    df = df[df["Area"] > 0]
    df["Yield"] = df["Production"] / df["Area"]

    if not df.empty:
        q1 = df["Yield"].quantile(0.01)
        q99 = df["Yield"].quantile(0.99)
        df = df[(df["Yield"] >= q1) & (df["Yield"] <= q99)]

    df = df.drop_duplicates()

    return df


def append_to_database(record):
    columns = ["State", "District", "Crop", "Season", "Year", "Area", "Production"]
    record_df = pd.DataFrame([{
        "State": record["State"].strip().title(),
        "District": record["District"].strip().title(),
        "Crop": record["Crop"].strip().title(),
        "Season": record["Season"].strip().title(),
        "Year": int(record["Year"]),
        "Area": float(record["Area"]),
        "Production": float(record["Production"])
    }])

    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        record_df.to_csv(DATA_PATH, mode="a", header=False, index=False)
    else:
        record_df.to_csv(DATA_PATH, mode="w", header=True, index=False)


@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(columns=["State", "District", "Crop", "Season", "Year", "Area", "Production", "Yield"])
    df = pd.read_csv(DATA_PATH)
    return preprocess_data(df)

def filter_data(df, state, district, crop, season, year_range):
    subset = df[(df["State"] == state) & (df["Crop"] == crop) & (df["Season"] == season)]
    subset = subset[(subset["Year"] >= year_range[0]) & (subset["Year"] <= year_range[1])]
    district_subset = subset[subset["District"] == district] if district != "All" else subset
    return subset, district_subset

def compute_estimates(data_used, area):
    grouped = data_used.groupby("Year")["Yield"].mean().reset_index()
    years = grouped["Year"].astype(int)
    yields = grouped["Yield"]
    avg_yield = data_used["Yield"].mean()
    production_avg = avg_yield * area

    trend_yield = avg_yield
    trend_production = production_avg
    trend_direction = "stable"
    if len(grouped) >= 2:
        x = years
        y = yields
        coefficients = np.polyfit(x, y, 1)
        slope = coefficients[0]
        poly = np.poly1d(coefficients)
        latest_year = x.max()
        predicted_yield = poly(latest_year)
        predicted_yield = max(predicted_yield, 0)
        trend_yield = predicted_yield
        trend_production = trend_yield * area
        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

    std_dev = data_used["Yield"].std()
    stability = "Low risk"
    if std_dev > data_used["Yield"].mean() * 0.5:
        stability = "High risk"
    elif std_dev > data_used["Yield"].mean() * 0.2:
        stability = "Medium risk"

    return avg_yield, production_avg, trend_yield, trend_production, trend_direction, stability, years, yields

def get_top_crops(df, state, season, year_range):
    subset = df[(df["State"] == state) & (df["Season"] == season)]
    subset = subset[(subset["Year"] >= year_range[0]) & (subset["Year"] <= year_range[1])]
    top = subset.groupby("Crop")["Yield"].mean().sort_values(ascending=False).head(5)
    return top

def make_trend_plot(years, yields):
    plt.figure(figsize=(7, 3.5))
    plt.plot(years, yields, marker="o", linestyle="-", color="#1f77b4", label="Historical yield")
    if len(years.unique()) >= 2:
        x = years
        y = yields
        coefs = np.polyfit(x, y, 1)
        poly = np.poly1d(coefs)
        xfit = np.arange(min(x), max(x) + 1)
        plt.plot(xfit, poly(xfit), color="orange", linestyle="--", label="Trend")
    plt.xlabel("Year")
    plt.ylabel("Yield")
    plt.title("Yield Trend")
    plt.grid(True, alpha=0.4)
    plt.legend()
    return plt

def make_comparison_chart(crop1_yield, crop2_yield, crop1, crop2):
    crops = [crop1, crop2]
    yields = [crop1_yield, crop2_yield]
    plt.figure(figsize=(6, 4))
    plt.bar(crops, yields, color=['blue', 'green'])
    plt.ylabel("Average Yield")
    plt.title("Crop Comparison")
    return plt

def create_card(title, value, subtitle):
    return f"""
<div class="card">
<h3>{title}</h3>
<p class="value">{value}</p>
<p class="subtitle">{subtitle}</p>
</div>
"""

def main():
    st.markdown(css, unsafe_allow_html=True)

    st.title(":bar_chart: YieldSense - Crop Yield Peer Analysis")
    st.markdown("Compare crop yields against peers in their region and season.")

    df = load_data()

    # Create two columns
    col_left, col_right = st.columns([1, 3])

    with col_left:
        # Inputs
        with st.container(border=True):
            st.subheader("Select Filters")

            states = sorted(df["State"].dropna().unique())
            state = st.selectbox("State", ["Select state"] + states, key="state")

            seasons = ["Kharif", "Rabi", "Zaid"]
            season = "Select season"

            # Season info
            with st.expander("Season Information"):
                st.markdown("""
                | Season  | Sowing Time | Harvesting Time | Key Examples |
                |---------|-------------|-----------------|--------------|
                | Kharif | June–July   | Sep–Oct         | Rice, Cotton, Maize |
                | Rabi   | Oct–Nov     | Mar–Apr         | Wheat, Mustard, Gram |
                | Zaid   |             |                 |             |
                """)

            if state != "Select state":
                available_seasons = df[df["State"] == state]["Season"].dropna().unique()
                valid_seasons = [s for s in seasons if s in available_seasons]
                if not valid_seasons:
                    st.warning(f"No valid seasons (Kharif, Rabi, Zaid) found in data for {state}.")
                else:
                    season = st.selectbox("Season", ["Select season"] + valid_seasons, key="season")

            selected_crop = "All"
            selected_crops = []
            top_auto_crops = []
            if state != "Select state" and season != "Select season":
                crops = sorted(df[(df["State"] == state) & (df["Season"] == season)]["Crop"].dropna().unique())
                selected_crop = st.selectbox("Crop for Prediction (optional)", ["All"] + crops, index=0, key="selected_crop")

                years = sorted(df["Year"].dropna().unique())
                year_options = ["1 Year", "3 Years", "5 Years", "10 Years", "All"]
                year_horizon = st.radio("Time Horizon", year_options, index=2, key="horizon")

                area = st.slider("Area (hectare)", min_value=0.01, max_value=100.0, value=1.0, step=0.01, key="area")

                # Map to year range
                current_year = int(max(years))
                if year_horizon == "1 Year":
                    start_year = current_year - 1
                elif year_horizon == "3 Years":
                    start_year = current_year - 3
                elif year_horizon == "5 Years":
                    start_year = current_year - 5
                elif year_horizon == "10 Years":
                    start_year = current_year - 10
                else:
                    start_year = int(min(years))
                year_range = (max(start_year, int(min(years))), current_year)

                # Determine top auto crops by historical average yield in the state/season/year range
                filtered_state_season = df[(df["State"] == state) & (df["Season"] == season) & (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
                if selected_crop == "All":
                    top_auto_crops = list(filtered_state_season.groupby("Crop")["Yield"].mean().sort_values(ascending=False).head(5).index)
                else:
                    top_auto_crops = [selected_crop] + list(filtered_state_season[filtered_state_season["Crop"] != selected_crop].groupby("Crop")["Yield"].mean().sort_values(ascending=False).head(4).index)

                selected_crops = top_auto_crops

                # prediction dataset
                filtered_state_season = df[(df["State"] == state) & (df["Season"] == season) & (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
                pred_df = filtered_state_season if selected_crop == "All" else filtered_state_season[filtered_state_season["Crop"] == selected_crop]

                # base prediction for selected crop (optional)
                if not pred_df.empty:
                    pred_avg, pred_prod, pred_trend_yield, pred_trend_production, pred_trend_direction, pred_stability, _, _ = compute_estimates(pred_df, area)

                    with st.container(border=True):
                        st.subheader("Yield Prediction")
                        prediction_col1, prediction_col2 = st.columns(2)
                        with prediction_col1:
                            st.metric("Predicted Yield per ha", f"{pred_trend_yield:.3f}", f"{pred_trend_direction.capitalize()} trend")
                        with prediction_col2:
                            st.metric("Predicted Production", f"{pred_trend_production:.3f}", f"for {area:.2f} ha")

                        st.write(f"**Stability:** {pred_stability}")
                        st.write(f"Forecast base: {('All crops' if selected_crop == 'All' else selected_crop)} | Year range: {year_range[0]}-{year_range[1]}")

                # top3 data (moved to main column)
                top3_options = selected_crops if selected_crops else list(crops)
                top3_candidates = []
                for c in top3_options:
                    candidate_df = df[(df["State"] == state) & (df["Season"] == season) & (df["Crop"] == c) & (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
                    if not candidate_df.empty:
                        _, _, c_trend_yield, c_trend_production, c_trend_direction, c_stability, _, _ = compute_estimates(candidate_df, area)
                        top3_candidates.append({
                            "Crop": c,
                            "TrendYield": c_trend_yield,
                            "Production": c_trend_production,
                            "Direction": c_trend_direction,
                            "Stability": c_stability,
                            "Records": len(candidate_df)
                        })

                top3_sorted = sorted(top3_candidates, key=lambda x: x["TrendYield"], reverse=True)[:3]

        if selected_crops:
            # Compute metrics
            best_crop = None
            best_yield = -np.inf
            worst_crop = None
            worst_yield = np.inf
            for crop in selected_crops:
                subset = df[(df["State"] == state) & (df["Crop"] == crop) & (df["Season"] == season) & (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
                if not subset.empty:
                    avg_y = subset["Yield"].mean()
                    if avg_y > best_yield:
                        best_yield = avg_y
                        best_crop = crop
                    if avg_y < worst_yield:
                        worst_yield = avg_y
                        worst_crop = crop

            with st.container(border=True):
                st.subheader("Key Metrics")
                st.metric("Best Crop", best_crop, f"{best_yield:.3f}")
                st.metric("Worst Crop", worst_crop, f"{worst_yield:.3f}")

    with col_right:
        if selected_crops and state != "Select state" and season != "Select season":
            # Prepare data for charts
            chart_data = []
            for crop in selected_crops:
                subset = df[(df["State"] == state) & (df["Crop"] == crop) & (df["Season"] == season) & (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
                if not subset.empty:
                    subset = subset.sort_values("Year")
                    yields = subset["Yield"].values
                    if len(yields) > 0:
                        normalized = yields / yields[0]  # Normalize to start at 1.0
                        for i, year in enumerate(subset["Year"]):
                            chart_data.append({"Year": int(year), "Normalized Yield": normalized[i], "Crop": crop})

            if chart_data:
                chart_df = pd.DataFrame(chart_data)

                # Large chart
                st.subheader("Normalized Yield Trends")
                line_chart = alt.Chart(chart_df).mark_line().encode(
                    x=alt.X("Year:O", title="Year"),
                    y=alt.Y("Normalized Yield:Q", title="Normalized Yield", scale=alt.Scale(zero=False)),
                    color="Crop:N",
                    tooltip=["Year", "Normalized Yield", "Crop"]
                ).properties(height=400)
                st.altair_chart(line_chart, use_container_width=True)

                # Top 3 crops to plant (middle section)
                if top3_sorted:
                    with st.container(border=True):
                        st.subheader("Top 3 Crops to Plant")
                        top3_cols = st.columns(3)
                        for idx, item in enumerate(top3_sorted):
                            with top3_cols[idx]:
                                st.metric(f"{idx+1}. {item['Crop']}", f"{item['TrendYield']:.3f} t/ha", f"{item['Direction'].capitalize()}, {item['Stability']}")

                        best_df = pd.DataFrame(top3_sorted)
                        bar = alt.Chart(best_df).mark_bar(color="#2E7D32").encode(
                            x=alt.X("Crop:N", sort="-y", title="Crop"),
                            y=alt.Y("TrendYield:Q", title="Predicted Yield (t/ha)"),
                            tooltip=["Crop", "TrendYield", "Production", "Direction", "Stability", "Records"]
                        ).properties(height=300)
                        st.altair_chart(bar, use_container_width=True)

                        st.write("**Why these crops?**")
                        for item in top3_sorted:
                            direction = "improving" if item['Direction'] == 'increasing' else "falling" if item['Direction'] == 'decreasing' else "steady"
                            stability_label = item['Stability'].replace('High risk', 'less predictable, watch weather/market').replace('Medium risk', 'moderately steady').replace('Low risk', 'very stable')
                            st.write(f"- {item['Crop']}: this is a top pick with predicted yield around {item['TrendYield']:.3f} t/ha, status {direction}, and stability profile {stability_label} (based on {item['Records']} historical records).")

                # Add new row to database
                with st.expander("Add new record to database"):
                    add_state = st.text_input("State", value=state if state != "Select state" else "")
                    add_district = st.text_input("District")
                    add_crop = st.text_input("Crop", value=selected_crop if selected_crop != "All" else "")
                    add_season = st.text_input("Season", value=season if season != "Select season" else "")
                    add_year = st.number_input("Year", min_value=1900, max_value=2100, value=int(current_year), step=1)
                    add_area = st.number_input("Area", min_value=0.01, max_value=10000.0, value=1.0, step=0.01)
                    add_production = st.number_input("Production", min_value=0.0, value=0.0, step=0.1)

                    if st.button("Add record"):
                        if not add_state or not add_crop or not add_season or add_year <= 0 or add_area <= 0 or add_production <= 0:
                            st.warning("Fill all fields with valid values before adding.")
                        else:
                            record = {
                                "State": add_state,
                                "District": add_district,
                                "Crop": add_crop,
                                "Season": add_season,
                                "Year": int(add_year),
                                "Area": float(add_area),
                                "Production": float(add_production)
                            }
                            append_to_database(record)
                            load_data.clear()
                            st.success("Record added successfully. Reloading data...")
                            st.experimental_rerun()

                # Individual comparisons
                st.subheader("Individual Crops vs Peer Average")
                # Compute peer avg for each crop
                peer_data = []
                for crop in selected_crops:
                    crop_df = chart_df[chart_df["Crop"] == crop]
                    if not crop_df.empty:
                        other_crops = [c for c in selected_crops if c != crop]
                        if other_crops:
                            peer_avg = chart_df[chart_df["Crop"].isin(other_crops)].groupby("Year")["Normalized Yield"].mean().reset_index()
                            peer_avg["Crop"] = "Peer Average"
                            peer_avg["Type"] = "Peer"
                            crop_df_copy = crop_df.copy()
                            crop_df_copy["Type"] = "Individual"
                            combined = pd.concat([crop_df_copy, peer_avg])
                            peer_data.append((crop, combined))

                # Render per crop with readable charts
                for crop, data in peer_data:
                    with st.container(border=True):
                        st.markdown(f"### {crop} vs Peer Average")

                        vs_chart = alt.Chart(data).mark_line(point=True).encode(
                            x=alt.X("Year:Q", title="Year", axis=alt.Axis(labelAngle=0)),
                            y=alt.Y("Normalized Yield:Q", title="Normalized Yield", scale=alt.Scale(zero=False)),
                            color=alt.Color("Type:N", scale=alt.Scale(domain=["Individual", "Peer"], range=["#d62728", "#7f7f7f"])),
                            tooltip=["Year", "Normalized Yield", "Type"]
                        ).properties(height=300)
                        st.altair_chart(vs_chart, use_container_width=True)

                        individual = data[data["Type"] == "Individual"].set_index("Year")["Normalized Yield"]
                        peer = data[data["Type"] == "Peer"].set_index("Year")["Normalized Yield"]
                        delta = (individual - peer).reset_index()
                        delta.columns = ["Year", "Delta"]

                        delta_chart = alt.Chart(delta).mark_area(opacity=0.4, color="#2E7D32").encode(
                            x=alt.X("Year:Q", title="Year", axis=alt.Axis(labelAngle=0)),
                            y=alt.Y("Delta:Q", title="Delta (Individual - Peer)"),
                            tooltip=["Year", "Delta"]
                        ).properties(height=220)
                        st.altair_chart(delta_chart, use_container_width=True)

                # Raw data
                st.subheader("Raw Data")
                st.dataframe(chart_df)

        else:
            st.info("Select state, season, and crops to view analysis.")

if __name__ == "__main__":
    main()

