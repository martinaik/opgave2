# Import necessary libraries
import os
import matplotlib.pyplot as plt
import pandas as pd
from app.database import get_connection

def create_correlation_heatmap() -> None:
    """ Creates a heatmap of correlations between selected DMI weather parameters. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch the relevant weather parameters from the measurement table
            cur.execute("""
                SELECT
                    temp_dry,
                    temp_dew,
                    humidity,
                    pressure_at_sea,
                    wind_speed,
                    precip_past10min,
                    visibility,
                    cloud_cover,
                    radia_glob
                FROM measurement
            """)
            rows = cur.fetchall()
            columns = [description.name for description in cur.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    # Convert all columns to numeric, coercing errors to NaN
    df = df.apply(pd.to_numeric, errors="coerce")

    # Drop columns that are entirely NaN
    df = df.dropna(axis=1, how="all")

    # Check if there are enough data points to compute correlations
    if len(df) < 10 or df.shape[1] < 2:
        print("There are not enough data points to compute correlations. At least 10 observations and 2 variables are required.")
        return

    # Calculate the Pearson correlation matrix, requiring at least 10 non-NaN observations for each pair of variables
    correlation = df.corr(method="pearson", min_periods=10)

    # Define labels for the heatmap axes
    labels = {
        "temp_dry": "Air temperature",
        "temp_dew": "Dew point temperature",
        "humidity": "Humidity",
        "pressure_at_sea": "Atmospheric pressure",
        "wind_speed": "Wind speed",
        "precip_past10min": "Precipitation (past 10 minutes)",
        "visibility": "Visibility",
        "cloud_cover": "Cloud cover",
        "radia_glob": "Global radiation",
    }

    correlation = correlation.rename(
        index=labels,
        columns=labels,
    )

    # Plot the heatmap
    fig, ax = plt.subplots(figsize=(11, 9))
    image = ax.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(correlation.columns)))
    ax.set_yticks(range(len(correlation.index)))
    ax.set_xticklabels(correlation.columns, rotation=45, ha="right")
    ax.set_yticklabels(correlation.index)

    # Annotate the heatmap with correlation values
    for i in range(len(correlation.index)):
        for j in range(len(correlation.columns)):
            value = correlation.iloc[i, j]

            if pd.notna(value):
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="black", fontsize=8)
            else:
                ax.text(j, i, "N/A", ha="center", va="center", color="black", fontsize=8)

    fig.colorbar(image, ax=ax, label="Pearson-correlation coefficient")
    ax.set_title("Correlation Heatmap of Selected DMI Weather Parameters")
    fig.tight_layout()

    # Ensure the output directory exists
    os.makedirs("/output/plots", exist_ok=True) 
    
    # Create a unique filename for the output plot
    number = 1
    while os.path.exists(f"/output/plots/correlation_heatmap{number}.png"):
        number += 1
    output_path = f"/output/plots/correlation_heatmap{number}.png"

    # Save the plot to a file
    plt.savefig(output_path, dpi=150)
    plt.close()

    # Print the path to the saved heatmap
    print(f"\nHeatmap saved as {output_path}")

# Run the function if this script is executed directly
if __name__ == "__main__":
    create_correlation_heatmap()
