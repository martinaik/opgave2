# Import necessary libraries
import os
import matplotlib.pyplot as plt
import pandas as pd
from app.database import get_connection

def create_temperature_boxplot() -> None:
    """ Creates a boxplot of temperatures across DMI stations. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch temperature measurements from the measurement table
            cur.execute("""
                SELECT station_id, temp_dry
                FROM measurement
                WHERE temp_dry IS NOT NULL
                ORDER BY station_id
            """)
            rows = cur.fetchall()

    # Check if any measurements were found
    if not rows:
        print("There are no temperature measurements in the database.")
        return

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=["station_id", "temp_dry"])
    df["temp_dry"] = pd.to_numeric(df["temp_dry"], errors="coerce")
    df = df.dropna(subset=["temp_dry"])

    # Check if there are valid temperature measurements
    if df.empty:
        print("There are no valid temperature measurements.")
        return

    # Sort stations by median temperature
    station_medians = df.groupby("station_id")["temp_dry"].median()
    stations = station_medians.sort_values().index.tolist()

    # Prepare the temperature data for each station
    temperatures = [
        df.loc[df["station_id"] == station, "temp_dry"].tolist()
        for station in stations
    ]

    # Make the figure taller when there are many stations
    figure_height = max(7, len(stations) * 0.35)

    # Create the boxplot
    fig, ax = plt.subplots(figsize=(12, figure_height))

    ax.boxplot(
        temperatures,
        orientation="horizontal",
        tick_labels=stations,
        showfliers=True,
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 2},
    )

    ax.set_title("Temperature Variation Across DMI Stations", pad=15)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Weather station")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
        
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/temperature_boxplot{number}.png"):
        number += 1
    output_path = f"/output/plots/temperature_boxplot{number}.png"
    
    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved boxplot
    print(f"\nBoxplot saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    create_temperature_boxplot()
