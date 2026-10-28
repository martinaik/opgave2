# Import necessary libraries
import os
import matplotlib.pyplot as plt
from app.database import get_connection

def plot_humidity_all_stations() -> None:
    """ Plots humidity over time for all stations with non-null values. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch all non-null humidity measurements for all stations
            cur.execute(
                """
                SELECT station_id, observed, humidity
                FROM dmi_measurement
                WHERE humidity IS NOT NULL
                ORDER BY observed;
                """
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print("No humidity measurements found.")
        return

    # Organize the measurements by station ID
    stations = {}

    for station_id, observed, humidity in rows:
        if station_id not in stations:
            stations[station_id] = {
                "timestamps": [],
                "humidity": [],
            }

        stations[station_id]["timestamps"].append(observed)
        stations[station_id]["humidity"].append(float(humidity))

    # Print the statistics for all stations
    print("\nHumidity statistics for all stations")
    print("=" * 75)
    print(
        f"{'Station':<12}"
        f"{'Measurements':>15}"
        f"{'Average (%)':>15}"
        f"{'Minimum (%)':>15}"
        f"{'Maximum (%)':>15}"
    )
    print("-" * 75)

    # Calculate and print statistics for each station
    for station_id, data in sorted(stations.items()):
        values = data["humidity"]

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

    # Print the average humidity for each station
    station_averages = {
        station_id: sum(data["humidity"]) / len(data["humidity"])
        for station_id, data in stations.items()
    }

    # Sort the stations by average humidity
    sorted_stations = sorted(
        station_averages.items(),
        key=lambda item: item[1],
    )

    station_ids = [item[0] for item in sorted_stations]
    averages = [item[1] for item in sorted_stations]

    # Plot the average humidity for each station
    plt.figure(figsize=(12, max(6, len(station_ids) * 0.3)))
    plt.barh(station_ids, averages)
    plt.title("Average humidity by weather station")
    plt.xlabel("Average humidity (%)")
    plt.ylabel("Station ID")
    plt.xlim(0, 100)
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 

    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/humidity_all_stations_{number}.png"):
        number += 1
    output_path = f"/output/plots/humidity_all_stations_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved graph
    print(f"\nGraph saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    plot_humidity_all_stations()
