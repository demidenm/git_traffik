import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.switch_backend('Agg')  # Turn off back end display to create plots

# Set your variables from the environmental info
owner = os.getenv('OWNER')
repo = os.getenv('REPO')
token = os.getenv('MY_ACCESS_TOKEN')

# Output data
csv_file = f'output/{repo}_git-trafficdata.csv'

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
os.makedirs('output', exist_ok=True)

# Get existing data if CSV file exists
if os.path.exists(csv_file):
    traffic_df = pd.read_csv(csv_file)
else:
    traffic_df = pd.DataFrame()

# Get views & clones data
views_data = get_data(views_url)
clones_data = get_data(clones_url)

# Convert views data to DataFrame and merge/update traffic_df
if views_data:
    views_df = pd.DataFrame(views_data['views'])
    views_df['timestamp'] = pd.to_datetime(views_df['timestamp'])
    views_df = views_df.rename(columns={'count': 'views_count', 'uniques': 'views_uniques'})

# Convert clones data to DataFrame and merge/update traffic_df
if clones_data:
    clones_df = pd.DataFrame(clones_data['clones'])
    clones_df['timestamp'] = pd.to_datetime(clones_df['timestamp'])
    clones_df = clones_df.rename(columns={'count': 'clones_count', 'uniques': 'clones_uniques'})

merged_viewsclones = pd.merge(views_df, clones_df, on='timestamp', how='outer')
# After outer join, fill na's with zeros
merged_viewsclones = merged_viewsclones.fillna(0)

# Save updated traffic_df to CSV
concatenated_df = pd.concat([traffic_df, merged_viewsclones], ignore_index=True)
concatenated_df['timestamp'] = concatenated_df['timestamp'].astype(str).str.split(' ').str[0]
uniq_df = concatenated_df.drop_duplicates(subset=['timestamp'])
uniq_df.to_csv(csv_file, index=False)


# Create plots

## Set Seaborn style and context
sns.set(style='whitegrid', font='Arial', rc={"axes.labelsize": 14, "xtick.labelsize": 12, "ytick.labelsize": 12})

## Create a figure with subplots
plt.figure(figsize=(12, 8))

## Plot views_count and views_uniques
plt.subplot(2, 1, 1)
plt.plot(uniq_df['timestamp'], uniq_df['views_count'], label='Views Count')
plt.plot(uniq_df['timestamp'], uniq_df['views_uniques'], label='Views Uniques')
plt.title('Views Count and Uniques Over Time', fontsize=16)
plt.xlabel('Timestamp', fontsize=14)
plt.ylabel('Count', fontsize=14)
plt.xticks(rotation=90)
plt.legend()

## Plot clones_count and clones_uniques
plt.subplot(2, 1, 2)
plt.plot(uniq_df['timestamp'], uniq_df['clones_count'], label='Clones Count')
plt.plot(uniq_df['timestamp'], uniq_df['clones_uniques'], label='Clones Uniques')
plt.title('Clones Count and Uniques Over Time', fontsize=16)
plt.xlabel('Timestamp', fontsize=14)
plt.ylabel('Count', fontsize=14)
plt.xticks(rotation=90)
plt.legend()

## Save plot
plt.tight_layout()
plt.savefig(f'output/{repo}_traffic-data.png', dpi=300)
plt.close()