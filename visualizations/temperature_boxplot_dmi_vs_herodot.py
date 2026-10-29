# Import necessary libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
from app.database import get_connection
from visualizations.get_danish_stations import get_danish_station_ids

def visualize_temperature_boxplot():
    """ Compares average indoor and outdoor temperature distributions. """

    # Get station IDs for stations in Denmark
    danish_station_ids = get_danish_station_ids()

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Get DMI outdoor temperatures
            cur.execute(
                """
                SELECT station_id, observed, temp_dry
                FROM dmi_measurement
                WHERE temp_dry IS NOT NULL
                ORDER BY observed
                """
            )
            rows = cur.fetchall()
            columns = [column.name for column in cur.description]
            dmi = pd.DataFrame(rows, columns=columns)

            # Get Herodot indoor temperatures
            cur.execute(
                """
                SELECT observed, temperature
                FROM herodot_measurement
                WHERE temperature IS NOT NULL
                ORDER BY observed
                """
            )
            rows = cur.fetchall()
            columns = [column.name for column in cur.description]
            herodot = pd.DataFrame(rows, columns=columns)

    # Check if data was retrieved from both sources
    if dmi.empty or herodot.empty:
        print("No temperature data available from DMI or Herodot.")
        return

    # Keep only Danish DMI stations
    dmi["station_id"] = dmi["station_id"].astype(str)
    danish_station_ids = {
        str(station_id) for station_id in danish_station_ids
    }
    dmi = dmi[dmi["station_id"].isin(danish_station_ids)].copy()

    # Check if there are any Danish DMI stations left after filtering
    if dmi.empty:
        print("No temperature measurements available from Danish DMI stations.")
        return

    # Convert timestamps to datetime
    dmi["observed"] = pd.to_datetime(dmi["observed"])
    herodot["observed"] = pd.to_datetime(herodot["observed"])

    # Keep only dates where both sources have measurements
    dmi["date"] = dmi["observed"].dt.date
    herodot["date"] = herodot["observed"].dt.date

    # Find common dates between DMI and Herodot measurements
    common_dates = set(dmi["date"]) & set(herodot["date"])

    # Keep only measurements from common dates
    dmi = dmi[dmi["date"].isin(common_dates)].copy()
    herodot = herodot[herodot["date"].isin(common_dates)].copy()

    # Check if there are any common dates left after filtering
    if dmi.empty or herodot.empty:
        print("No common dates with data from both data sources.")
        return

    # Group measurements into 10-minute intervals
    dmi["time_interval"] = dmi["observed"].dt.floor("10min")
    herodot["time_interval"] = herodot["observed"].dt.floor("10min")

    # Calculate average outdoor temperature across Danish stations
    dmi_avg = (
        dmi.groupby("time_interval")["temp_dry"]
        .mean()
        .rename("outdoor_temperature")
    )

    # Calculate average indoor temperature across Herodot measurements
    herodot_avg = (
        herodot.groupby("time_interval")["temperature"]
        .mean()
        .rename("indoor_temperature")
    )

    # Keep only intervals with measurements from both sources
    combined = pd.concat([dmi_avg, herodot_avg], axis=1).dropna()

    # Check if there are any matching intervals left after filtering
    if combined.empty:
        print("No matching 10-minute intervals found.")
        return

    # Prepare the temperature data for the boxplot
    temperature_data = [
        combined["outdoor_temperature"].values,
        combined["indoor_temperature"].values,
    ]

    # Create the boxplot
    fig, ax = plt.subplots(figsize=(9, 6))

    ax.boxplot(
        temperature_data,
        tick_labels=[
            "Outdoor temperature (DMI)",
            "Indoor temperature (Herodot)",
        ],
        showfliers=True,
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 2},
    )

    ax.set_title("Temperature Variation: Indoor vs. Outdoor", pad=15)
    ax.set_xlabel("Data source")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True)

    # Create a unique filename
    number = 1
    while os.path.exists(f"/output/plots/temperature_boxplot_dmi_vs_herodot{number}.png"):
        number += 1
    output_path = (f"/output/plots/temperature_boxplot_dmi_vs_herodot{number}.png")

    # Save the plot
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    # Print the output path
    print(f"\nTemperature boxplot saved as {output_path}")

# Run the visualization function if this script is executed directly
if __name__ == "__main__":
    visualize_temperature_boxplot()
