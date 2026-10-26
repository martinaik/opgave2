# Import necessary libraries
import os
from statistics import mean
import matplotlib.pyplot as plt
from app.database import get_connection

def plot_wind_speed(station_id: str = "06108") -> None:
    """ Plots DMI wind speed measurements for one weather station. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch all non-null wind speed measurements for the specified station
            cur.execute(
                """
                SELECT observed, wind_speed
                FROM measurement
                WHERE wind_speed IS NOT NULL
                  AND station_id = %s
                ORDER BY observed;
                """,
                (station_id,),
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print(f"No wind speed measurements found for station {station_id}.")
        return

    # Extract timestamps and wind speed values
    timestamps = [row[0] for row in rows]
    wind_values = [float(row[1]) for row in rows]

    # Calculate statistics
    average_wind = mean(wind_values)
    min_wind = min(wind_values)
    max_wind = max(wind_values)
    number_of_measurements = len(wind_values)
    
    # Print the statistics
    print(f"\nWind speed statistics for station {station_id}")
    print("-" * 45)
    print(f"Number of measurements: {number_of_measurements}")
    print(f"Average wind speed: {average_wind:.2f} m/s")
    print(f"Minimum wind speed: {min_wind:.2f} m/s")
    print(f"Maximum wind speed: {max_wind:.2f} m/s")

    # Plot the wind speed measurements over time
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, wind_values, marker="o", markersize=3, label="Wind speed")
    plt.axhline(average_wind, linestyle="--", label=f"Average: {average_wind:.2f} m/s")
    plt.title(f"DMI wind speed over time - Station {station_id}")
    plt.xlabel("Time")
    plt.ylabel("Wind speed (m/s)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/wind_speed_plot_{number}.png"):
        number += 1
    output_path = f"/output/plots/wind_speed_plot_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved plot
    print(f"\nGraph saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    plot_wind_speed()
