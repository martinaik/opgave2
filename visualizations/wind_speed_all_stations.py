# Import necessary libraries
import os
import matplotlib.pyplot as plt
from app.database import get_connection

def plot_wind_all_stations() -> None:
    """ Plots wind speed over time for all stations with non-null values. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch all non-null wind speed measurements for all stations
            cur.execute(
                """
                SELECT station_id, observed, wind_speed
                FROM dmi_measurement
                WHERE wind_speed IS NOT NULL
                ORDER BY observed;
                """
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print("No wind speed measurements found.")
        return

    # Organize the measurements by station ID
    stations = {}

    for station_id, observed, wind_speed in rows:
        if station_id not in stations:
            stations[station_id] = {
                "timestamps": [],
                "wind_speed": [],
            }

        stations[station_id]["timestamps"].append(observed)
        stations[station_id]["wind_speed"].append(float(wind_speed))

    # Print the statistics for all stations
    print("\nWind speed statistics for all stations")
    print("=" * 75)
    print(
        f"{'Station':<12}"
        f"{'Measurements':>15}"
        f"{'Average (m/s)':>15}"
        f"{'Minimum (m/s)':>15}"
        f"{'Maximum (m/s)':>15}"
    )
    print("-" * 75)

    # Calculate and print statistics for each station
    for station_id, data in sorted(stations.items()):
        values = data["wind_speed"]

        print(
            f"{station_id:<12}"
            f"{len(values):>15}"
            f"{sum(values) / len(values):>15.2f}"
            f"{min(values):>15.2f}"
            f"{max(values):>15.2f}"
        )

    print("=" * 75)
    print(f"Number of stations: {len(stations)}")
    print(f"Total measurements: {len(rows)}")

    # Print the average wind speed for each station
    station_averages = {
        station_id: sum(data["wind_speed"]) / len(data["wind_speed"])
        for station_id, data in stations.items()
    }

    # Sort the stations by average wind speed
    sorted_stations = sorted(
        station_averages.items(),
        key=lambda item: item[1],
    )

    station_ids = [item[0] for item in sorted_stations]
    averages = [item[1] for item in sorted_stations]

    # Plot the average wind speed for each station
    plt.figure(figsize=(12, max(6, len(station_ids) * 0.3)))
    plt.barh(station_ids, averages)
    plt.title("Average wind speed by weather station")
    plt.xlabel("Average wind speed (m/s)")
    plt.ylabel("Station ID")
    plt.xlim(0, 40)
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/wind_speed_all_stations_{number}.png"):
        number += 1
    output_path = f"/output/plots/wind_speed_all_stations_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved graph
    print(f"\nGraph saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    plot_wind_all_stations()
