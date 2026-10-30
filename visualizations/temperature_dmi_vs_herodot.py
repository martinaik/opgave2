# Import necessary libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from app.database import get_connection
from visualizations.get_danish_stations import get_danish_station_ids

def visualize_temperature_comparison():
    """ Compares outdoor DMI temperatures with indoor Herodot temperatures. """

    # Get station IDs for stations in Denmark
    danish_station_ids = get_danish_station_ids()

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Get DMI temperatures
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

            # Get Herodot temperatures
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
        print("Der mangler temperaturdata fra DMI eller Herodot.")
        return

    # Keep only Danish DMI stations
    dmi["station_id"] = dmi["station_id"].astype(str)
    danish_station_ids = {str(station_id) for station_id in danish_station_ids}
    dmi = dmi[dmi["station_id"].isin(danish_station_ids)].copy()

    # Check if there are any Danish DMI stations left after filtering
    if dmi.empty:
        print("No Danish DMI temperature measurements available.")
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
        print("Ingen fælles datoer med data fra både DMI og Herodot.")
        return

    # Group measurements into 10-minute intervals
    dmi["time_bin"] = dmi["observed"].dt.floor("10min")
    herodot["time_bin"] = herodot["observed"].dt.floor("10min")

    # Calculate average temperature for each interval
    dmi_avg = dmi.groupby("time_bin")["temp_dry"].mean()
    herodot_avg = herodot.groupby("time_bin")["temperature"].mean()

    # Combine the two temperature series
    combined = pd.concat(
        [
            dmi_avg.rename("Outdoor temperature (DMI)"),
            herodot_avg.rename("Indoor temperature (Herodot)"),
        ],
        axis=1,
    ).sort_index()

    # Plot temperatures
    ax = combined.plot(figsize=(12, 6))
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title("Outdoor temperature vs. indoor temperature")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M"))
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True)

    # Create a unique filename for the plot
    number = 1
    while os.path.exists(f"/output/plots/temperature_dmi_vs_herodot{number}.png"):
        number += 1
    output_path = (f"/output/plots/temperature_dmi_vs_herodot{number}.png")

    # Save the plot
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the output path
    print(f"\nTemperature comparison saved as {output_path}")

# Run the visualization function if this script is executed directly
if __name__ == "__main__":
    visualize_temperature_comparison()
