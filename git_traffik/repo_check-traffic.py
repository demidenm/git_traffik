import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.switch_backend('Agg')  # Turn off back end display to create plots

# Set your variables from the environmental info
owner = os.getenv('OWNER')
repo = os.getenv('REPO')
token = os.getenv('MY_ACCESS_TOKEN')

# Define the output directory and CSV file path
output_dir = 'git_traffik/output'
csv_file = os.path.join(output_dir, f'{repo}_git-trafficdata.csv')

views_url = f'https://api.github.com/repos/{owner}/{repo}/traffic/views'
clones_url = f'https://api.github.com/repos/{owner}/{repo}/traffic/clones'

headers = {
    'Authorization': f'token {token}'
}

# Function to get data from a given git URL
def get_data(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get data: {response.status_code} - {response.text}")
        return None

# Create output folder if it does not exist
os.makedirs(output_dir, exist_ok=True)

# Get existing data if CSV file exists
if os.path.exists(csv_file):
    traffic_df = pd.read_csv(csv_file)
else:
    traffic_df = pd.DataFrame()

# Get views & clones data
views_data = get_data(views_url)
clones_data = get_data(clones_url)

# Convert views data & clones data to pandas df and them process
views_df = pd.DataFrame(views_data.get('views', []))  # Use .get to handle missing 'views' key
clones_df = pd.DataFrame(clones_data.get('clones', []))  


# Process 'timestamp' column if it exists
if 'timestamp' in views_df.columns:
    views_df['timestamp'] = pd.to_datetime(views_df['timestamp']).dt.tz_convert('UTC')
else:
    views_df['timestamp'] = np.nan  

if 'timestamp' in clones_df.columns:
    clones_df['timestamp'] = pd.to_datetime(clones_df['timestamp']).dt.tz_convert('UTC')
else:
    clones_df['timestamp'] = np.nan  

# Rename columns if they exist
views_df = views_df.rename(columns={
    'count': 'views_count', 
    'uniques': 'views_uniques'
}).reindex(columns=['timestamp', 'views_count', 'views_uniques'], fill_value=np.nan)  

clones_df = clones_df.rename(columns={
    'count': 'clones_count', 
    'uniques': 'clones_uniques'
}).reindex(columns=['timestamp', 'clones_count', 'clones_uniques'], fill_value=np.nan)


# create timestamp range and merge
views_df['timestamp'] = pd.to_datetime(views_df['timestamp'], errors='coerce')
clones_df['timestamp'] = pd.to_datetime(clones_df['timestamp'], errors='coerce')

start_date = min(views_df['timestamp'].min(), clones_df['timestamp'].min())

# Ensure start_date is not NaT, otherwise use a default value (e.g., today's date) + set end date
if pd.isna(start_date):
    start_date = pd.Timestamp.now(tz='UTC')

end_date = pd.Timestamp.now(tz='UTC')

# Generate the full date range, get df with full range data
full_date_range = pd.date_range(start=start_date, end=end_date, tz='UTC')
date_df = pd.DataFrame({'timestamp': full_date_range})

# Merge views and clones dataframes with the full date range. NAs --> 0
merged_viewsclones = pd.merge(date_df, views_df, on='timestamp', how='left')
merged_viewsclones = pd.merge(merged_viewsclones, clones_df, on='timestamp', how='left')

merged_viewsclones = merged_viewsclones.fillna({
    'views_count': 0, 
    'views_uniques': 0, 
    'clones_count': 0, 
    'clones_uniques': 0
})

# Sort by timestamp in ascending order, then convert it to a string (keeping only the date part)
# reset index after
merged_viewsclones = merged_viewsclones.sort_values(by='timestamp')
merged_viewsclones['timestamp'] = merged_viewsclones['timestamp'].astype(str).str.split(' ').str[0]

merged_viewsclones = merged_viewsclones.reset_index(drop=True)

# Combine with the existing traffic_df (if one existed)
concatenated_df = pd.concat([traffic_df, merged_viewsclones], ignore_index=True)
uniq_df = concatenated_df.drop_duplicates(subset=['timestamp'])

print(f"Saving CSV to: {csv_file}")
uniq_df.to_csv(csv_file, index=False)


# Create plots
# spacing for x-axis ticks -- at large n things overcrowd
data_length = len(uniq_df)
tick_interval = max(1, data_length // 10)  # lower value more tick labels

# Create plots
sns.set(style='whitegrid', context='talk', rc={"axes.labelsize": 14, "xtick.labelsize": 12, "ytick.labelsize": 12})
plt.figure(figsize=(14, 10))

# Plot views_count and views_uniques
plt.subplot(2, 1, 1)
plt.plot(uniq_df['timestamp'], uniq_df['views_count'], label='Views Count', linewidth=2.5, linestyle='-', color=sns.color_palette('muted')[0])
plt.plot(uniq_df['timestamp'], uniq_df['views_uniques'], label='Views Uniques', linewidth=2.5, linestyle='--', color=sns.color_palette('muted')[1])
plt.title('Views Count and Uniques Over Time', fontsize=18)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Count', fontsize=14)
plt.xticks(ticks=uniq_df.index[::tick_interval], labels=uniq_df['timestamp'].dt.strftime('%Y-%m-%d').iloc[::tick_interval], rotation=90)
plt.legend(fontsize=12, loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)

# Plot clones_count and clones_uniques
plt.subplot(2, 1, 2)
plt.plot(uniq_df['timestamp'], uniq_df['clones_count'], label='Clones Count', linewidth=2.5, linestyle='-', color=sns.color_palette('muted')[2])
plt.plot(uniq_df['timestamp'], uniq_df['clones_uniques'], label='Clones Uniques', linewidth=2.5, linestyle='--', color=sns.color_palette('muted')[3])
plt.title('Clones Count and Uniques Over Time', fontsize=18)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Count', fontsize=14)
plt.xticks(ticks=uniq_df.index[::tick_interval], labels=uniq_df['timestamp'].dt.strftime('%Y-%m-%d').iloc[::tick_interval], rotation=90)
plt.legend(fontsize=12, loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)

# Improve layout and save plot
plt.tight_layout()
plot_path = os.path.join(output_dir, f'{repo}_traffic-data.png')
plt.savefig(plot_path, dpi=300)
plt.close()

if os.path.exists(plot_path):
    print(f"File saved successfully: {plot_path}")
else:
    print(f"File not saved: {plot_path}")
