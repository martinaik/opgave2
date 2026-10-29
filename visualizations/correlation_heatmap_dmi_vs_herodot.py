# Import necessary libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
from app.database import get_connection
from visualizations.get_danish_stations import get_danish_station_ids

def visualize_correlation_heatmap():
    """ Creates a heatmap showing the correlation between DMI and Herodot temperature and humidity measurements. """

    # Get station IDs for stations in Denmark
    danish_station_ids = get_danish_station_ids()

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Get DMI temperature and humidity
            cur.execute(
                """
                SELECT station_id, observed, temp_dry, humidity
                FROM dmi_measurement
                WHERE temp_dry IS NOT NULL
                   OR humidity IS NOT NULL
                ORDER BY observed
                """
            )
            rows = cur.fetchall()
            columns = [column.name for column in cur.description]
            dmi = pd.DataFrame(rows, columns=columns)

            # Get Herodot temperature and humidity
            cur.execute(
                """
                SELECT observed, temperature, humidity
                FROM herodot_measurement
                WHERE temperature IS NOT NULL
                   OR humidity IS NOT NULL
                ORDER BY observed
                """
            )
            rows = cur.fetchall()
            columns = [column.name for column in cur.description]
            herodot = pd.DataFrame(rows, columns=columns)

    # Check if data was retrieved from both sources
    if dmi.empty or herodot.empty:
        print("No temperature or humidity data available from DMI or Herodot.")
        return

    # Keep only Danish DMI stations
    dmi["station_id"] = dmi["station_id"].astype(str)
    dmi = dmi[dmi["station_id"].isin(danish_station_ids)].copy()

    # Check if there are any Danish DMI stations left after filtering
    if dmi.empty:
        print("No Danish DMI stations found.")
        return

    # Convert timestamps to datetime
    dmi["observed"] = pd.to_datetime(dmi["observed"])
    herodot["observed"] = pd.to_datetime(herodot["observed"])

    # Extract the date from each measurement
    dmi["date"] = dmi["observed"].dt.date
    herodot["date"] = herodot["observed"].dt.date

    # Find common dates between DMI and Herodot measurements
    common_dates = set(dmi["date"]) & set(herodot["date"])

    # Keep only dates where both sources have measurements
    dmi = dmi[dmi["date"].isin(common_dates)].copy()
    herodot = herodot[herodot["date"].isin(common_dates)].copy()

    # Check if there are any common dates left after filtering
    if dmi.empty or herodot.empty:
        print("No common dates with data from both DMI and Herodot.")
        return

    # Calculate average DMI values across Danish stations at each timestamp
    dmi_avg = (
        dmi.groupby(["date", "observed"], as_index=False)[
            ["temp_dry", "humidity"]
        ]
        .mean()
        .rename(
            columns={
                "temp_dry": "DMI temperature",
                "humidity": "DMI humidity",
            }
        )
    )

    # Average Herodot values if multiple measurements share a timestamp
    herodot_avg = (
        herodot.groupby(["date", "observed"], as_index=False)[
            ["temperature", "humidity"]
        ]
        .mean()
        .rename(
            columns={
                "temperature": "Herodot temperature",
                "humidity": "Herodot humidity",
            }
        )
    )

    # Match measurements from the same date within 10 minutes
    dmi_avg = dmi_avg.sort_values("observed")
    herodot_avg = herodot_avg.sort_values("observed")

    combined = pd.merge_asof(
        dmi_avg,
        herodot_avg,
        on="observed",
        by="date",
        direction="nearest",
        tolerance=pd.Timedelta("10min"),
    )

    # Keep rows where both sources have all four measurements
    variables = [
        "DMI temperature",
        "DMI humidity",
        "Herodot temperature",
        "Herodot humidity",
    ]

    combined = combined.dropna(subset=variables)

    # Check if there are enough matched measurements to calculate correlations
    if len(combined) < 2:
        print("Not enough matched measurements to calculate correlations.")
        return

    # Calculate Pearson correlation coefficients
    correlation = combined[variables].corr(method="pearson")

    # Check if any correlation values are NaN
    if correlation.isna().any().any():
        print(
            "Not enough data to calculate correlations for all variable pairs."
        )
        return

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(10, 8))

    image = ax.imshow(
        correlation,
        vmin=-1,
        vmax=1,
        cmap="coolwarm",
        aspect="equal",
    )

    # Add variable names to the axes
    labels = [
        "DMI temperature",
        "DMI humidity",
        "Herodot temperature",
        "Herodot humidity",
    ]

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    # Display correlation coefficients inside each cell
    for row in range(len(labels)):
        for col in range(len(labels)):
            value = correlation.iloc[row, col]
            text_color = "white" if abs(value) > 0.55 else "black"

            ax.text(
                col,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=11,
            )

    ax.set_title("Correlation Heatmap of DMI vs. Herodot", pad=15)

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Pearson-correlation coefficient")

    fig.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True)

    # Create a unique filename
    number = 1
    while os.path.exists(f"/output/plots/correlation_heatmap_dmi_vs_herodot{number}.png"):
        number += 1
    output_path = (f"/output/plots/correlation_heatmap_dmi_vs_herodot{number}.png")

    # Save the heatmap
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    # Print the output path
    print(f"\nCorrelation heatmap saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    visualize_correlation_heatmap()
