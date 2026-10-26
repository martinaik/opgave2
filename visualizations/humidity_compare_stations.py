# Import necessary libraries
import os
from statistics import mean
import matplotlib.pyplot as plt
from app.database import get_connection

def compare_humidity_stations(station_ids: list[str] | None = None) -> None:
    """ Compares humidity over time for selected weather stations. """

    # If no station IDs are provided, use default station IDs
    if station_ids is None:
        station_ids = ["06108", "06110", "06120"]

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch humidity measurements for the specified stations
            cur.execute(
                """
                SELECT station_id, observed, humidity
                FROM measurement
                WHERE humidity IS NOT NULL
                  AND station_id = ANY(%s)
                ORDER BY observed;
                """,
                (station_ids,),
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print("No humidity measurements found for the selected stations.")
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

    # Print the statistics for the selected stations
    print("\nHumidity statistics for selected stations")
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
    for station_id in station_ids:
        if station_id not in stations:
            print(f"{station_id:<12}{'No data':>15}")
            continue

        values = stations[station_id]["humidity"]

        print(
            f"{station_id:<12}"
            f"{len(values):>15}"
            f"{mean(values):>15.2f}"
            f"{min(values):>15.2f}"
            f"{max(values):>15.2f}"
        )

    print("=" * 75)

    # Plot the humidity measurements for each station
    plt.figure(figsize=(12, 6))

    for station_id in station_ids:
        if station_id not in stations:
            continue

        data = stations[station_id]

        plt.plot(data["timestamps"], data["humidity"], label=station_id, marker="o", markersize=2)

    plt.title("Air humidity over time - Selected DMI stations")
    plt.xlabel("Time")
    plt.ylabel("Air humidity (%)")
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.legend(title="Station")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 

    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/humidity_comparison_{number}.png"):
        number += 1
    output_path = f"/output/plots/humidity_comparison_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved graph
    print(f"\nGraph saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    compare_humidity_stations()
