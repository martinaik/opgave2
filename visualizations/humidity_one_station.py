# Import necessary libraries
import os
from statistics import mean
import matplotlib.pyplot as plt
from app.database import get_connection

def plot_humidity(station_id: str = "06108") -> None:
    """ Plot DMI humidity measurements for one weather station. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch humidity measurements for the specified station
            cur.execute(
                """
                SELECT observed, humidity
                FROM dmi_measurement
                WHERE humidity IS NOT NULL
                  AND station_id = %s
                ORDER BY observed;
                """,
                (station_id,),
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print(f"No humidity measurements found for station {station_id}.")
        return

    # Get timestamps and humidity values from the query results
    timestamps = [row[0] for row in rows]
    humidity_values = [float(row[1]) for row in rows]

    # Calculate statistics
    average_humidity = mean(humidity_values)
    min_humidity = min(humidity_values)
    max_humidity = max(humidity_values)
    number_of_measurements = len(humidity_values)
  
    # Print the statistics for the selected station
    print(f"\nHumidity statistics for station {station_id}")
    print("-" * 45) 
    print(f"Number of measurements: {number_of_measurements}")
    print(f"Average humidity: {average_humidity:.2f} %")
    print(f"Minimum humidity: {min_humidity:.2f} %")
    print(f"Maximum humidity: {max_humidity:.2f} %")

    # Plot the humidity measurements over time
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, humidity_values, marker="o", markersize=3, label="Humidity")
    plt.axhline(average_humidity, linestyle="--", label=f"Average: {average_humidity:.2f} %")
    plt.title(f"DMI humidity over time - Station {station_id}")
    plt.xlabel("Time")
    plt.ylabel("Air humidity (%)")
    plt.ylim(0, 100)
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/humidity_plot_{number}.png"):
        number += 1
    output_path = f"/output/plots/humidity_plot_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved graph
    print(f"\nGraph saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    plot_humidity()
