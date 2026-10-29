# Import necessary libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
from app.database import get_connection
from visualizations.get_danish_stations import get_danish_station_ids

def visualize_humidity_comparison():
    """ Compares outdoor DMI humidity with indoor Herodot humidity. """

    # Get station IDs for stations in Denmark
    danish_station_ids = get_danish_station_ids()

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Get DMI humidity
            cur.execute(
                """
                SELECT station_id, observed, humidity
                FROM dmi_measurement
                WHERE humidity IS NOT NULL
                ORDER BY observed
                """
            )
            rows = cur.fetchall()
            columns = [column.name for column in cur.description]
            dmi = pd.DataFrame(rows, columns=columns)

            # Get Herodot humidity
            cur.execute(
                """
                SELECT observed, humidity
                FROM herodot_measurement
                WHERE humidity IS NOT NULL
                ORDER BY observed
                """
            )
            rows = cur.fetchall()
            columns = [column.name for column in cur.description]
            herodot = pd.DataFrame(rows, columns=columns)

    # Check if data was retrieved from both sources
    if dmi.empty or herodot.empty:
        print("No humidity data available from DMI or Herodot.")
        return

    # Keep only Danish DMI stations
    dmi["station_id"] = dmi["station_id"].astype(str)
    danish_station_ids = {str(station_id) for station_id in danish_station_ids}
    dmi = dmi[dmi["station_id"].isin(danish_station_ids)].copy()

    # Check if there are any Danish DMI stations left after filtering
    if dmi.empty:
        print("No humidity measurements available from Danish DMI stations.")
        return

    # Convert timestamps to datetime
    dmi["observed"] = pd.to_datetime(dmi["observed"])
    herodot["observed"] = pd.to_datetime(herodot["observed"])

    # Extract the date from each measurement
    dmi["date"] = dmi["observed"].dt.date
    herodot["date"] = herodot["observed"].dt.date

    # Find dates where both sources have measurements
    common_dates = set(dmi["date"]) & set(herodot["date"])

    # Keep measurements from common dates
    dmi = dmi[dmi["date"].isin(common_dates)].copy()
    herodot = herodot[herodot["date"].isin(common_dates)].copy()

    # Check if there are any common dates left after filtering
    if dmi.empty or herodot.empty:
        print("No common dates with data from both DMI and Herodot.")
        return

    # Group measurements into 10-minute intervals
    dmi["time_bin"] = dmi["observed"].dt.floor("10min")
    herodot["time_bin"] = herodot["observed"].dt.floor("10min")

    # Calculate average humidity for each interval
    dmi_avg = dmi.groupby("time_bin")["humidity"].mean()
    herodot_avg = herodot.groupby("time_bin")["humidity"].mean()

    # Combine the two humidity series
    combined = pd.concat(
        [
            dmi_avg.rename("Outdoor humidity (DMI)"),
            herodot_avg.rename("Indoor humidity (Herodot)"),
        ],
        axis=1,
    ).sort_index()

    # Plot humidity
    combined.plot(figsize=(12, 6))
    plt.xlabel("Time")
    plt.ylabel("Humidity (%)")
    plt.title("Outdoor humidity vs. indoor humidity")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True)

    # Create a unique filename for the plot
    number = 1
    while os.path.exists(f"/output/plots/humidity_dmi_vs_herodot{number}.png"):
        number += 1
    output_path = (f"/output/plots/humidity_dmi_vs_herodot{number}.png")

    # Save the plot
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the output path
    print(f"\nHumidity comparison saved as {output_path}")

# Run the visualization function if this script is executed directly
if __name__ == "__main__":
    visualize_humidity_comparison()
