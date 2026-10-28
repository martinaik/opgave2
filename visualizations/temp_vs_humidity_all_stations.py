# Import necessary libraries
import os
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from app.database import get_connection

def plot_temp_humidity_correlation_all_stations() -> None:
    """ Calculates and plots temperature-humidity correlation for all stations. """

    # Connect to the databse
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch all non-null temperature and humidity measurements for all stations
            cur.execute(
                """
                SELECT station_id, temp_dry, humidity
                FROM dmi_measurement
                WHERE temp_dry IS NOT NULL
                  AND humidity IS NOT NULL
                ORDER BY station_id;
                """
            )
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print("No complete temperature and humidity measurements found.")
        return

    # Organize measurements by station
    stations = {}

    for station_id, temperature, humidity in rows:
        if station_id not in stations:
            stations[station_id] = {
                "temperatures": [],
                "humidity": [],
            }

        stations[station_id]["temperatures"].append(float(temperature))
        stations[station_id]["humidity"].append(float(humidity))

    correlations = []

    # Print header for correlation results
    print("\nTemperature vs. humidity correlation by station")
    print("=" * 65)
    print(
        f"{'Station':<12}"
        f"{'Measurements':>15}"
        f"{'Correlation':>15}"
        f"{'P-value':>15}"
    )
    print("-" * 65)

    # Calculate correlation for each station
    for station_id, data in stations.items():
        temperatures = data["temperatures"]
        humidity_values = data["humidity"]

        # Check if there are enough varying measurements to calculate correlation
        if (
            len(temperatures) < 2
            or len(set(temperatures)) < 2
            or len(set(humidity_values)) < 2
        ):
            continue

        correlation, p_value = pearsonr(temperatures, humidity_values)

        correlations.append((station_id, correlation, p_value, len(temperatures)))

    # Sort the correlations by correlation value
    correlations.sort(key=lambda item: item[1])

    # Print the correlation results for each station
    for station_id, correlation, p_value, count in correlations:
        print(
            f"{station_id:<12}"
            f"{count:>15}"
            f"{correlation:>15.3f}"
            f"{p_value:>15.4f}"
        )

    print("=" * 65)
    print(f"Stations with calculated correlations: {len(correlations)}")

    # Check if there are any stations with enough varying data to calculate correlation
    if not correlations:
        print("No stations had enough varying data to calculate correlation.")
        return

    # Plot the correlation values for all stations
    station_ids = [item[0] for item in correlations]
    correlation_values = [item[1] for item in correlations]

    plt.figure(figsize=(12, max(6, len(station_ids) * 0.3)))
    plt.barh(station_ids, correlation_values)
    plt.axvline(x=0, color="black", linestyle="--", linewidth=1)
    plt.title("Temperature vs. humidity correlation - All stations")
    plt.xlabel("Pearson correlation coefficient")
    plt.ylabel("Station ID")
    plt.xlim(-1, 1)
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/temp_humidity_correlation_all_stations_{number}.png"):
        number += 1
    output_path = f"/output/plots/temp_humidity_correlation_all_stations_{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved graph
    print(f"\nGraph saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    plot_temp_humidity_correlation_all_stations()
