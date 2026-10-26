# Import necessary libraries
import os
from statistics import mean
import matplotlib.pyplot as plt
from app.database import get_connection

def compare_stations(station_ids: list[str] | None = None) -> None:
    """ Compares temperature measurements from multiple DMI stations. """

    # If no station IDs are provided, use default station IDs
    if station_ids is None:
        station_ids = ["06108", "06110", "06120"]

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch temperature measurements for the specified stations
            cur.execute(
                """
                SELECT station_id, observed, temp_dry
                FROM measurement
                WHERE temp_dry IS NOT NULL
                  AND station_id = ANY(%s)
                ORDER BY observed;
                """,
                (station_ids,),
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print("No temperature measurements found.")
        return

    # Organize the measurements by station ID
    station_data: dict[str, list[tuple]] = {
        station_id: [] for station_id in station_ids
    }

    for station_id, observed, temperature in rows:
        station_data[station_id].append(
            (observed, float(temperature))
        )

    # Print the statistics for the selected stations
    print("\nTemperature statistics for selected stations")
    print("=" * 75)
    print(
        f"{'Station':<10}"
        f"{'Measurements':>14}"
        f"{'Average °C':>14}"
        f"{'Minimum °C':>14}"
        f"{'Maximum °C':>14}"
    )
    print("-" * 75)
    
    # Plot the temperature measurements for each station
    plt.figure(figsize=(12, 6))

    for station_id, measurements in station_data.items():
        # Check if there are measurements for the station
        if not measurements:
            print(f"No measurements for station {station_id}.")
            continue

        # Extract timestamps and temperatures for the station
        timestamps = [row[0] for row in measurements]
        temperatures = [row[1] for row in measurements]

        # Plot the temperature measurements for the station
        plt.plot(timestamps, temperatures, marker="o", markersize=2, label=f"Station {station_id}")

        # Print the statistics for the station
        print(
            f"{station_id:<10}"
            f"{len(temperatures):>14}"
            f"{mean(temperatures):>14.2f}"
            f"{min(temperatures):>14.2f}"
            f"{max(temperatures):>14.2f}"
        )

    print("=" * 75)

    # Set the title, labels, and legend for the plot
    plt.title("DMI temperature comparison between stations")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(
        f"/output/plots/temperature_comparison_{number}.png"
    ):
        number += 1
    output_path = f"/output/plots/temperature_comparison_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved plot
    print(f"\nComparison graph saved as {output_path}")

# Run the comparison if the script is executed directly
if __name__ == "__main__":
    compare_stations()
