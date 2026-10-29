# Import necessary libraries
import os
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from app.database import get_connection

def plot_temperature_vs_wind(station_id: str = "06108") -> None:
    """ Plots temperature against wind speed for one weather station. """

    # Connec to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch all non-null temperature and wind speed measurements for the specified station
            cur.execute(
                """
                SELECT temp_dry, wind_speed
                FROM dmi_measurement
                WHERE temp_dry IS NOT NULL
                  AND wind_speed IS NOT NULL
                  AND station_id = %s
                ORDER BY observed;
                """,
                (station_id,),
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print(
            f"No complete temperature and wind speed measurements "
            f"found for station {station_id}."
        )
        return

    # Extract temperature and wind speed values
    temperatures = [float(row[0]) for row in rows]
    wind_speed_values = [float(row[1]) for row in rows]

    # Calculate Pearson correlation coefficient and p-value
    if len(rows) < 2:
        print("Not enough measurements to calculate correlation.")
        return

    correlation, p_value = pearsonr(temperatures, wind_speed_values)

    print(f"\nPearson correlation: {correlation:.3f}")
    print(f"P-value: {p_value:.4f}")

    if correlation > 0:
        print("The variables have a positive correlation.")
    elif correlation < 0:
        print("The variables have a negative correlation.")
    else:
        print("No linear correlation was found.")

    # Print the number of measurements
    print(f"\nTemperature vs. wind speed - Station {station_id}")
    print("-" * 45)
    print(f"Number of measurements: {len(rows)}")

    # Plot the temperature vs. wind speed scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(temperatures, wind_speed_values, alpha=0.6, label="Measurements")
    plt.title(f"Temperature vs. wind speed - Station {station_id}")
    plt.xlabel("Temperature (°C)")
    plt.ylabel("Wind speed (m/s)")
    plt.ylim(0, 20)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(
        f"/output/plots/temperature_vs_wind_speed_{number}.png"
    ):
        number += 1
    output_path = f"/output/plots/temperature_vs_wind_speed_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved plot
    print(f"\nGraph saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    plot_temperature_vs_wind()
