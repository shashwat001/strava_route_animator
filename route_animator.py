import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import contextily as ctx
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import logging
from matplotlib.patches import FancyBboxPatch

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Haversine formula to calculate distance between two points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# GPX file exported from Strava
# Step 1: Parse the GPX file
logging.info("Parsing GPX file")
gpx_file = open('Casual_Evening_City_ride.gpx', 'r')
gpx = gpxpy.parse(gpx_file)

# Extract coordinates
logging.info("Extracting coordinates")
coords = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            coords.append((point.longitude, point.latitude))

# Calculate the bounding box
logging.info("Calculating bounding box")
min_lon = min(coord[0] for coord in coords)
max_lon = max(coord[0] for coord in coords)
min_lat = min(coord[1] for coord in coords)
max_lat = max(coord[1] for coord in coords)

# Wide area for zoom out effect
wide_min_lon = min_lon - 0.1
wide_max_lon = max_lon + 0.1
wide_min_lat = min_lat - 0.1
wide_max_lat = max_lat + 0.1

# Add a buffer around the route
buffer_percentage = 0.3  # Maintain this buffer size for better spacing
lon_range = max_lon - min_lon
lat_range = max_lat - min_lat
buffer_lon = lon_range * buffer_percentage
buffer_lat = lat_range * buffer_percentage

min_lon -= buffer_lon
max_lon += buffer_lon
min_lat -= buffer_lat
max_lat += buffer_lat

# Calculate aspect ratio of the route
route_width = max_lon - min_lon
route_height = max_lat - min_lat
aspect_ratio = route_width / route_height

# Calculate total distance using Haversine formula
logging.info("Calculating total distance")
total_distance = 0.0
for i in range(1, len(coords)):
    total_distance += haversine(coords[i-1][1], coords[i-1][0], coords[i][1], coords[i][0])
    if i % 100 == 0:  # Log progress every 100 points
        logging.info(f"Processed {i} points")

logging.info(f"Total distance: {total_distance:.2f} km")

# Create a figure with the correct aspect ratio and higher DPI
fig_width = 10  # Adjust this base width if needed
fig_height = fig_width / aspect_ratio
fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)

# Set the initial extent of the map (wide area)
ax.set_xlim(wide_min_lon, wide_max_lon)
ax.set_ylim(wide_min_lat, wide_max_lat)

# Remove axes and frame
ax.axis('off')
ax.set_frame_on(False)

# Add the basemap with a higher zoom level for better resolution using OpenStreetMap tiles
logging.info("Adding basemap")
ctx.add_basemap(ax, crs='EPSG:4326', source=ctx.providers.OpenStreetMap.Mapnik, zoom=13)

# Create empty line with thicker linewidth and light green color
line, = ax.plot([], [], lw=3, color='red')
# Create the marker using scatter
marker = ax.scatter([], [], color='red', s=100)  # Adjust the size (s) as needed

# Reduce the number of frames by sampling the coordinates
sample_rate = 10  # Adjust this value to change the speed (higher value = faster animation)
coords_sampled = coords[::sample_rate]

# Calculate total number of frames and fading parameters
total_frames = len(coords_sampled)
fade_duration = 2 * 30  # Assuming 30 fps, last 2 seconds
fade_start_frame = total_frames - fade_duration

# Additional frames to maintain the last frame for 5 seconds (assuming 30 fps)
hold_duration = 5 * 30

# Additional frames for zoom-in effect (3 seconds at 30 fps)
zoom_duration = 3 * 30

# Initial hold duration for showing activity name and start time
initial_hold_duration = 2 * 30  # 2 seconds at 30 fps

# Total number of frames, including hold frames
total_frames += hold_duration + zoom_duration + initial_hold_duration

# Set activity name and start time
activity_name = "Morning Ride"
start_time = "2024-06-30 06:30 AM"

# Add the total distance text in bigger, bold font and dark purple color
distance_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=16, fontweight='bold', color='purple', ha='left', va='top')
activity_text = ax.text(0.5, 0.8, f"{activity_name}", transform=ax.transAxes, fontsize=20, fontweight='bold', color='darkorange', ha='center', va='center', alpha=0)
start_time_text = ax.text(0.5, 0.75, f"{start_time}", transform=ax.transAxes, fontsize=20, fontweight='bold', color='darkorange', ha='center', va='center', alpha=0)
background_box = FancyBboxPatch((0.3, 0.7), 0.4, 0.15, boxstyle="round,pad=0.3", transform=ax.transAxes, facecolor="lightyellow", edgecolor="none", alpha=0)

def init():
    line.set_data([], [])
    marker.set_offsets(np.array([[], []]).T)
    distance_text.set_text('')
    distance_text.set_alpha(0)
    activity_text.set_alpha(0)
    start_time_text.set_alpha(0)
    background_box.set_alpha(0)
    return line, marker, distance_text, activity_text, start_time_text, background_box

def animate(i):
    if i < initial_hold_duration:
        # Initial hold effect
        pass
    elif i < initial_hold_duration + zoom_duration:
        # Zoom-in effect
        frame_idx = i - initial_hold_duration
        current_min_lon = wide_min_lon + (min_lon - wide_min_lon) * (frame_idx / zoom_duration)
        current_max_lon = wide_max_lon + (max_lon - wide_max_lon) * (frame_idx / zoom_duration)
        current_min_lat = wide_min_lat + (min_lat - wide_min_lat) * (frame_idx / zoom_duration)
        current_max_lat = wide_max_lat + (max_lat - wide_max_lat) * (frame_idx / zoom_duration)
        ax.set_xlim(current_min_lon, current_max_lon)
        ax.set_ylim(current_min_lat, current_max_lat)
    elif i < len(coords_sampled) + initial_hold_duration + zoom_duration:
        # Route animation
        frame_idx = i - initial_hold_duration - zoom_duration
        x = [coord[0] for coord in coords_sampled[:frame_idx]]
        y = [coord[1] for coord in coords_sampled[:frame_idx]]
        line.set_data(x, y)
        if frame_idx > 0:  # Place the marker only when there's at least one point
            marker.set_offsets(np.array([[x[-1], y[-1]]]))
    else:
        # Hold the last frame
        frame_idx = i - initial_hold_duration - zoom_duration - len(coords_sampled)
        x = [coord[0] for coord in coords_sampled]
        y = [coord[1] for coord in coords_sampled]
        line.set_data(x, y)
        marker.set_offsets(np.array([[x[-1], y[-1]]]))

        # Zoom-out effect
        if frame_idx < zoom_duration:
            current_min_lon = min_lon + (wide_min_lon - min_lon) * (frame_idx / zoom_duration)
            current_max_lon = max_lon + (wide_max_lon - max_lon) * (frame_idx / zoom_duration)
            current_min_lat = min_lat + (wide_min_lat - min_lat) * (frame_idx / zoom_duration)
            current_max_lat = max_lat + (wide_max_lat - max_lat) * (frame_idx / zoom_duration)
            ax.set_xlim(current_min_lon, current_max_lon)
            ax.set_ylim(current_min_lat, current_max_lat)

    return line, marker, distance_text, activity_text, start_time_text, background_box

# Create the animation
logging.info("Creating animation")
ani = animation.FuncAnimation(fig, animate, init_func=init, frames=total_frames, interval=20, blit=True)

# Adjust the figure size to remove any padding
fig.tight_layout(pad=0)
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Save the first frame as a thumbnail image
logging.info("Saving thumbnail")
animate(0)
fig.savefig("thumbnail.png", bbox_inches='tight', pad_inches=0, dpi=300)

# Save the animation as an MP4 video
logging.info("Saving animation as MP4")
writer = animation.FFMpegWriter(fps=30)  # Increased fps for smoother animation
with writer.saving(fig, "route_animation.mp4", dpi=300):
    for i in range(total_frames):
        if i % 100 == 0:  # Log progress every 100 frames
            logging.info(f"Processing frame {i}/{total_frames}")
        animate(i)
        writer.grab_frame()

print("Route animation saved as route_animation.mp4")
logging.info("Animation saved successfully")
plt.close(fig)  # Close the figure to free up memory

# Debug information
logging.info(f"Map bounds: Longitude ({min_lon}, {max_lon}), Latitude ({min_lat}, {max_lat})")
logging.info(f"Map aspect ratio: {aspect_ratio}")
logging.info(f"Figure size: {fig_width} x {fig_height}")
logging.info(f"Total distance: {total_distance:.2f} km")
