import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import time, datetime
from tqdm import tqdm
import logging
from geopy.geocoders import Nominatim

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set seaborn style for better visuals
sns.set_style("whitegrid")
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'Arial',
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12
})

# Step 1: Read the CSV file with progress bar
logging.info("Loading CSV file...")
try:
    df = pd.read_csv('yellow_tripdata.csv')
except FileNotFoundError:
    logging.error("File 'yellow_tripdata.csv' not found. Please check the file path.")
    raise

# Step 2: Validate required columns
required_columns = ['tpep_pickup_datetime', 'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    logging.error(f"Missing required columns: {missing_columns}")
    raise ValueError(f"Missing required columns: {missing_columns}")

# Step 3: Log dataset statistics
logging.info(f"Dataset size: {len(df)} rows")
logging.info(f"Date range: {df['tpep_pickup_datetime'].min()} to {df['tpep_pickup_datetime'].max()}")

# Step 4: Parse the tpep_pickup_datetime column as datetime
df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')
if df['tpep_pickup_datetime'].isna().any():
    logging.warning(f"{df['tpep_pickup_datetime'].isna().sum()} rows with invalid datetime values dropped.")
    df = df.dropna(subset=['tpep_pickup_datetime'])

# Step 5: Filter for April 2016 (or March as test)
logging.info("Filtering for April 2016...")
df_april = df[
    (df['tpep_pickup_datetime'].dt.year == 2016) &
    (df['tpep_pickup_datetime'].dt.month == 4) &
    (df['tpep_pickup_datetime'].dt.day.isin([5, 19]))
]
logging.info(f"After April 5 and 19, 2016 filter: {len(df_april)} rows.")
if len(df_april) == 0:
    logging.warning("No April 2016 data found. Falling back to March 2016 as test.")
    df = df[
        (df['tpep_pickup_datetime'].dt.year == 2016) &
        (df['tpep_pickup_datetime'].dt.month == 3)
    ]
    logging.info(f"After March 2016 filter: {len(df)} rows.")
else:
    df = df_april

# Step 6: Extract time and day components
df['pickup_time'] = df['tpep_pickup_datetime'].dt.time
df['pickup_day'] = df['tpep_pickup_datetime'].dt.day
df['pickup_weekday'] = df['tpep_pickup_datetime'].dt.weekday

# Step 7: Define the time ranges
time_range1_start = time(19, 30)
time_range1_end = time(20, 15)
time_range2_start = time(22, 25)
time_range2_end = time(22, 35)

# Step 8: Filter for the specified time ranges and pickup locations
logging.info("Filtering for time ranges [19:30–20:15] and [22:25–22:35]...")

pickup_locations = [
    (40.7519, -73.9762),  # Hyatt (Park Ave & E 42nd St)
    (40.7521, -73.9770),  # Vanderbilt Ave & E 42nd St
    (40.7505, -73.9770),  # E 40th St & Park Ave
    #(40.762463, -73.988069), # TMPL HellKitchen
    #(40.729957, -73.992636), # TMPL AstorPlace
    #(40.758386, -73.970764), # TMPL Lexington
    (40.734220, -74.002206),  # TMPL West Village
]
def is_near_pickup(lat, lon, locations, threshold=0.005):  # ~500m threshold
    return any(abs(lat - loc[0]) < threshold and abs(lon - loc[1]) < threshold for loc in locations)

filtered_df = df[
    ((df['pickup_time'] >= time_range1_start) & (df['pickup_time'] <= time_range1_end)) |
    ((df['pickup_time'] >= time_range2_start) & (df['pickup_time'] <= time_range2_end))
].copy()
filtered_df['near_pickup'] = filtered_df.apply(
    lambda row: is_near_pickup(row['pickup_latitude'], row['pickup_longitude'], pickup_locations), axis=1
)
filtered_df = filtered_df[filtered_df['near_pickup']]
logging.info(f"After time range and pickup location filter: {len(filtered_df)} rows.")

# Step 9: Filter for sports club trips on Tuesdays
if not filtered_df.empty:
    tuesday_sports_club_df = filtered_df[
        (filtered_df['pickup_time'] >= time(20, 45)) &
        (filtered_df['pickup_time'] <= time(21, 15))
    ]
    logging.info(f"Sports club trips (Tuesdays): {len(tuesday_sports_club_df)} rows.")
else:
    tuesday_sports_club_df = pd.DataFrame()
    logging.warning("No data for sports club trips due to empty filtered_df.")

# Step 10: Validate coordinates
filtered_df = filtered_df.dropna(subset=['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude'])
filtered_df = filtered_df[
    (filtered_df['pickup_latitude'].between(40.5, 41.0)) &
    (filtered_df['pickup_longitude'].between(-74.3, -73.7)) &
    (filtered_df['dropoff_latitude'].between(40.5, 41.0)) &
    (filtered_df['dropoff_longitude'].between(-74.3, -73.7))
]
logging.info(f"After coordinate validation: {len(filtered_df)} rows.")

# Step 11: Identify frequent drop-off locations (potential home addresses)
if not filtered_df.empty:
    filtered_df['dropoff_lat_round'] = filtered_df['dropoff_latitude'].round(4)
    filtered_df['dropoff_lon_round'] = filtered_df['dropoff_longitude'].round(4)
    dropoff_counts = filtered_df.groupby(['dropoff_lat_round', 'dropoff_lon_round']).size().reset_index(name='count')
    top_dropoffs = dropoff_counts[dropoff_counts['count'] >= dropoff_counts['count'].quantile(0.95)]  # Top 5%

    # Reverse geocoding for top two drop-off locations
    geolocator = Nominatim(user_agent="taxi_analysis")
    for idx, row in top_dropoffs.sort_values(by='count', ascending=False).head(2).iterrows():
        location = geolocator.reverse((row['dropoff_lat_round'], row['dropoff_lon_round']), language='en')
        if location:
            top_dropoffs.at[idx, 'address'] = location.address
else:
    top_dropoffs = pd.DataFrame(columns=['dropoff_lat_round', 'dropoff_lon_round', 'count'])
    logging.warning("No valid data for drop-off analysis.")

# Step 12: Save the filtered data
filtered_df.to_csv('filtered_taxi_data.csv', index=False)

# Step 13: Create a Folium map with clustering, heatmap, and layer control for top drop-offs
logging.info("Creating Folium map...")
map_center = [40.7128, -74.0060] if filtered_df.empty else [
    filtered_df['pickup_latitude'].mean(),
    filtered_df['pickup_longitude'].mean()
]
m = folium.Map(location=map_center, zoom_start=12, tiles='CartoDB Positron')

# Add pickup cluster
pickup_cluster = MarkerCluster(name='Pickups').add_to(m)
if not filtered_df.empty:
    for _, row in tqdm(filtered_df.iterrows(), total=len(filtered_df), desc="Adding pickup markers"):
        try:
            folium.CircleMarker(
                location=[row['pickup_latitude'], row['pickup_longitude']],
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6,
                popup=folium.Popup(
                    f"Pickup Time: {row['tpep_pickup_datetime']}",
                    max_width=200
                )
            ).add_to(pickup_cluster)
        except Exception as e:
            logging.warning(f"Error adding pickup marker at {row['pickup_latitude']},{row['pickup_longitude']}: {e}")

# Add dropoff cluster (all dropoffs)
dropoff_cluster = MarkerCluster(name='All Dropoffs').add_to(m)
if not filtered_df.empty:
    for _, row in tqdm(filtered_df.iterrows(), total=len(filtered_df), desc="Adding dropoff markers"):
        try:
            folium.CircleMarker(
                location=[row['dropoff_latitude'], row['dropoff_longitude']],
                radius=5,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6,
                popup=folium.Popup(
                    f"Dropoff Time: {row['tpep_dropoff_datetime']}",
                    max_width=200
                )
            ).add_to(dropoff_cluster)
        except Exception as e:
            logging.warning(f"Error adding dropoff marker at {row['dropoff_latitude']},{row['dropoff_longitude']}: {e}")

# Add separate layers for top two drop-off locations with different colors
if not filtered_df.empty:
    # Identify top two drop-off locations
    if not top_dropoffs.empty:
        top_two = top_dropoffs.sort_values(by='count', ascending=False).head(2)
        for idx, (index, row) in enumerate(top_two.iterrows()):
            lat_lon = (row['dropoff_lat_round'], row['dropoff_lon_round'])
            color = 'orange' if idx == 0 else 'purple'
            layer_name = f'Top Dropoff {idx + 1} ({color.capitalize()})'
            layer = folium.FeatureGroup(name=layer_name).add_to(m)
            for _, row_data in tqdm(filtered_df.iterrows(), total=len(filtered_df), desc=f"Adding {layer_name} markers"):
                try:
                    if (round(row_data['dropoff_latitude'], 4), round(row_data['dropoff_longitude'], 4)) == lat_lon:
                        folium.CircleMarker(
                            location=[row_data['dropoff_latitude'], row_data['dropoff_longitude']],
                            radius=5,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.6,
                            popup=folium.Popup(
                                f"Dropoff Time: {row_data['tpep_dropoff_datetime']}",
                                max_width=200
                            )
                        ).add_to(layer)
                except Exception as e:
                    logging.warning(f"Error adding {layer_name} marker at {row_data['dropoff_latitude']},{row_data['dropoff_longitude']}: {e}")

# Add heatmap for all dropoffs
if not filtered_df.empty:
    heatmap_data = filtered_df[['dropoff_latitude', 'dropoff_longitude']].dropna().values
    HeatMap(heatmap_data, radius=10, blur=15, max_zoom=15, name='Dropoff Heatmap').add_to(m)

# Add layer control
folium.LayerControl().add_to(m)
m.save('taxi_pickup_dropoff_map.html')
logging.info("Map saved to 'taxi_pickup_dropoff_map.html'.")

# Step 14: Create an enhanced Matplotlib histogram
if not filtered_df.empty:
    logging.info("Creating histogram...")
    filtered_df['minutes_since_midnight'] = filtered_df['tpep_pickup_datetime'].dt.hour * 60 + filtered_df['tpep_pickup_datetime'].dt.minute

    plt.figure(figsize=(12, 7), facecolor='white')
    sns.histplot(
        data=filtered_df,
        x='minutes_since_midnight',
        bins=20,
        color='skyblue',
        edgecolor='navy',
        kde=True,
        line_kws={'linewidth': 2, 'color': 'darkblue'}
    )
    plt.title('Distribution of Taxi Pickups (2016)', fontsize=18, pad=20, weight='bold')
    plt.xlabel('Time (HH:MM)', fontsize=14)
    plt.ylabel('Number of Pickups', fontsize=14)

    tick_positions = [19*60+30, 20*60+15, 22*60+25, 22*60+35]
    tick_labels = ['19:30', '20:15', '22:25', '22:35']
    plt.xticks(tick_positions, tick_labels, rotation=45)

    plt.axvspan(19*60+30, 20*60+15, color='lightgreen', alpha=0.3, label='19:30-20:15 (Workplace)')
    plt.axvspan(22*60+25, 22*60+35, color='lightcoral', alpha=0.3, label='22:25-22:35 (Sports Club)')
    plt.legend(title='Time Ranges', loc='upper right', fontsize=12)

    peak_bin = filtered_df['minutes_since_midnight'].mode()[0]
    plt.annotate(
        'Peak Time',
        xy=(peak_bin, plt.ylim()[1] * 0.9),
        xytext=(peak_bin + 50, plt.ylim()[1] * 0.95),
        arrowprops=dict(facecolor='black', shrink=0.05),
        fontsize=12,
        color='darkred'
    )

    plt.tight_layout()
    plt.savefig('pickup_time_histogram.png', dpi=300, bbox_inches='tight')
    plt.show()
else:
    logging.warning("No data found in the specified time ranges. Histogram not generated.")

# Step 15: Drop temporary columns
filtered_df = filtered_df.drop(columns=['pickup_time', 'minutes_since_midnight', 'dropoff_lat_round', 'dropoff_lon_round', 'near_pickup'], errors='ignore')

# Step 16: Display results
print(f"Filtered {len(filtered_df)} rows.")
print("\nTop drop-off locations (potential home addresses):")
print(top_dropoffs.sort_values(by='count', ascending=False).head(10))
print("\nSample of sports club trips (Tuesdays):")
print(tuesday_sports_club_df[[
    'tpep_pickup_datetime', 'pickup_longitude', 'pickup_latitude',
    'dropoff_longitude', 'dropoff_latitude'
]].head())
print("\nSummary of Potential Home Addresses (Top 2):")
for idx, row in top_dropoffs.sort_values(by='count', ascending=False).head(2).iterrows():
    address = row.get('address', 'Address not found')
    print(f"Location {idx + 1}: Lat {row['dropoff_lat_round']}, Lon {row['dropoff_lon_round']}, Trips: {row['count']}, Approx. Address: {address}")
