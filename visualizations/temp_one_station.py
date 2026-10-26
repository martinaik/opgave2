# Import necessary libraries
import os
from statistics import mean
import matplotlib.pyplot as plt
from app.database import get_connection

def plot_temperature(station_id: str = "06108") -> None:
    """ Plots temperature measurements and calculate statistics for a station. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch temperature measurements for the specified station
            cur.execute(
                """
                SELECT observed, temp_dry
                FROM measurement
                WHERE temp_dry IS NOT NULL
                  AND station_id = %s
                ORDER BY observed;
                """,
                (station_id,),
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print(f"No temperature measurements found for station {station_id}.")
        return

    # Extract timestamps and temperature values
    timestamps = [row[0] for row in rows]
    temperatures = [float(row[1]) for row in rows]

    # Calculate statistics
    average_temp = mean(temperatures)
    min_temp = min(temperatures)
    max_temp = max(temperatures)
    number_of_measurements = len(temperatures)

    # Print statistics
    print(f"\nTemperature statistics for station {station_id}")
    print("-" * 45)
    print(f"Number of measurements: {number_of_measurements}")
    print(f"Average temperature: {average_temp:.2f} °C")
    print(f"Minimum temperature: {min_temp:.2f} °C")
    print(f"Maximum temperature: {max_temp:.2f} °C")

    # Plot the temperature measurements over time
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, temperatures, marker="o", markersize=3, label="Temperature")
    plt.axhline(average_temp, linestyle="--", label=f"Average: {average_temp:.2f} °C")
    plt.title(f"DMI temperature over time - Station {station_id}")
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
    while os.path.exists(f"/output/plots/temperature_plot_{number}.png"):
        number += 1
    output_path = f"/output/plots/temperature_plot_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved plot
    print(f"\nGraph saved as {output_path}")

# Run the plotting function if the script is executed directly
if __name__ == "__main__":
    plot_temperature()
