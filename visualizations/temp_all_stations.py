# Import necessary libraries
import os
import matplotlib.pyplot as plt
from app.database import get_connection

def compare_all_stations() -> None:
    """ Compares temperature statistics for all stations. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch temperature statistics for all stations
            cur.execute(
                """
                SELECT
                    station_id,
                    COUNT(*) AS number_of_measurements,
                    AVG(temp_dry) AS average_temperature,
                    MIN(temp_dry) AS minimum_temperature,
                    MAX(temp_dry) AS maximum_temperature
                FROM dmi_measurement
                WHERE temp_dry IS NOT NULL
                GROUP BY station_id
                ORDER BY AVG(temp_dry);
                """
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print("No temperature measurements found.")
        return

    # Print the statistics for all stations
    print("\nTemperature statistics for all stations")
    print("=" * 75)
    print(
        f"{'Station':<10}"
        f"{'Measurements':>14}"
        f"{'Average °C':>14}"
        f"{'Minimum °C':>14}"
        f"{'Maximum °C':>14}"
    )
    print("-" * 75)

    station_ids = []
    average_temperatures = []

    # Calculate and print statistics for each station
    for station_id, count, average, minimum, maximum in rows:
        station_ids.append(station_id)
        average_temperatures.append(float(average))

        print(
            f"{station_id:<10}"
            f"{count:>14}"
            f"{float(average):>14.2f}"
            f"{float(minimum):>14.2f}"
            f"{float(maximum):>14.2f}"
        )

    print("=" * 75)

    # Plot the average temperatures for all stations
    plt.figure(figsize=(12, max(8, len(rows) * 0.22)))
    plt.barh(station_ids, average_temperatures)
    plt.title("Average DMI temperature by weather station")
    plt.xlabel("Average temperature (°C)")
    plt.ylabel("Station ID")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(
        f"/output/plots/temperature_all_stations_{number}.png"
    ):
        number += 1
    output_path = f"/output/plots/temperature_all_stations_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved plot
    print(f"\nGraph saved as {output_path}")

# Run the comparison if the script is executed directly
if __name__ == "__main__":
    compare_all_stations()
