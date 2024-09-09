
Now, let me explain each part of this data collection and analysis process in detail:

Data Collection:

We use the requests library to fetch web pages from Pro-Football-Reference, a reliable source of NFL statistics.
BeautifulSoup is used to parse the HTML and extract the relevant tables.
We create separate functions to scrape passing, rushing, receiving, and defensive stats.
The data is collected for the last 5 NFL seasons to provide a good amount of historical data for our models.
Each year's data is saved as separate CSV files in a data/raw/ directory.


Data Preprocessing:

We load the raw CSV files for each statistic type.
The datasets are merged based on player names and teams, combining passing, rushing, and receiving stats for each player.
Missing values are filled with zeros, assuming that missing stats mean the player didn't accumulate any in that category.
We calculate fantasy points using a sample scoring system. You can adjust this formula based on your specific league rules.
The data from all years is combined into a single DataFrame.
We use StandardScaler from scikit-learn to scale the numeric features, which is important for many machine learning algorithms.


Exploratory Data Analysis:

We create a Jupyter Notebook to explore the processed data.
Basic statistics are computed to understand the distribution of each feature.
A correlation heatmap is created to visualize relationships between different statistics.
We plot the distribution of fantasy points to understand the overall scoring patterns.
Top players by average fantasy points are visualized in a bar plot.
Positional analysis is performed to compare fantasy point distributions across different positions.
Year-over-year trends are plotted to identify any long-term changes in scoring patterns.



This process sets a strong foundation for the rest of the project. Here's what you can do next:

Run the data collection script to gather the raw data.
Execute the preprocessing script to clean and combine the data.
Open the Jupyter Notebook and run the exploratory data analysis. This will give you insights into the data and help guide your feature engineering and model development process.
Based on the insights from the EDA, you might want to:

Create additional features (e.g., yards per attempt, touchdowns per game)
Investigate any anomalies or unexpected patterns in the data
Decide on which features are most important for predicting fantasy performance


The next step would be to start developing prediction models for each position, which we can dive into if you're ready to proceed.

Do you have any questions about this data collection and analysis process? Or would you like to move on to the next step of developing prediction models?

# Section 1: Data Collection and Analysis

## 1.1 Data Collection

First, let's create a script to scrape NFL data. We'll use the `requests` library to fetch web pages and `BeautifulSoup` for parsing HTML.

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def scrape_nfl_data(year):
    base_url = f"https://www.pro-football-reference.com/years/{year}/"
    
    # Scrape passing stats
    passing_df = scrape_table(base_url + "passing.htm", "passing")
    
    # Scrape rushing stats
    rushing_df = scrape_table(base_url + "rushing.htm", "rushing")
    
    # Scrape receiving stats
    receiving_df = scrape_table(base_url + "receiving.htm", "receiving")
    
    # Scrape defense stats
    defense_df = scrape_table(base_url + "defense.htm", "defense")
    
    return passing_df, rushing_df, receiving_df, defense_df

def scrape_table(url, stat_type):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'all_' + stat_type})
    
    df = pd.read_html(str(table))[0]
    df = df[df['Player'] != 'Player']  # Remove header rows
    df = df.dropna(how='all')  # Remove fully empty rows
    
    return df

# Scrape data for the last 5 years
current_year = 2023  # Update this annually
for year in range(current_year - 4, current_year + 1):
    passing, rushing, receiving, defense = scrape_nfl_data(year)
    
    # Save to CSV
    os.makedirs(f'data/raw/{year}', exist_ok=True)
    passing.to_csv(f'data/raw/{year}/passing.csv', index=False)
    rushing.to_csv(f'data/raw/{year}/rushing.csv', index=False)
    receiving.to_csv(f'data/raw/{year}/receiving.csv', index=False)
    defense.to_csv(f'data/raw/{year}/defense.csv', index=False)

print("Data collection complete.")
```

This script scrapes passing, rushing, receiving, and defensive stats for the last 5 NFL seasons and saves them as CSV files.

## 1.2 Data Preprocessing

Next, let's create a script to preprocess the collected data:

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(year):
    # Load data
    passing = pd.read_csv(f'data/raw/{year}/passing.csv')
    rushing = pd.read_csv(f'data/raw/{year}/rushing.csv')
    receiving = pd.read_csv(f'data/raw/{year}/receiving.csv')
    
    # Merge datasets
    players = pd.merge(passing, rushing, on=['Player', 'Tm'], how='outer', suffixes=('_pass', '_rush'))
    players = pd.merge(players, receiving, on=['Player', 'Tm'], how='outer')
    
    # Fill NaN values with 0 for numeric columns
    players = players.fillna(0)
    
    # Create fantasy points column (example scoring system)
    players['FantasyPoints'] = (
        players['Yds_pass'] * 0.04 +
        players['TD_pass'] * 4 +
        players['Int'] * -2 +
        players['Yds_rush'] * 0.1 +
        players['TD_rush'] * 6 +
        players['Rec'] * 1 +  # PPR
        players['Yds'] * 0.1 +
        players['TD'] * 6
    )
    
    return players

def scale_features(df):
    scaler = StandardScaler()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

# Process data for the last 5 years
current_year = 2023  # Update this annually
all_players = []

for year in range(current_year - 4, current_year + 1):
    players = load_and_preprocess_data(year)
    players['Year'] = year
    all_players.append(players)

# Combine all years
all_players_df = pd.concat(all_players, ignore_index=True)

# Scale features
all_players_scaled = scale_features(all_players_df)

# Save processed data
all_players_scaled.to_csv('data/processed/all_players_scaled.csv', index=False)

print("Data preprocessing complete.")
```

This script loads the raw data, merges datasets, calculates fantasy points, and scales the features.

## 1.3 Exploratory Data Analysis

Now, let's create a Jupyter Notebook for exploratory data analysis:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the processed data
df = pd.read_csv('data/processed/all_players_scaled.csv')

# Basic statistics
print(df.describe())

# Correlation heatmap
plt.figure(figsize=(20, 16))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Heatmap of NFL Player Statistics')
plt.show()

# Distribution of Fantasy Points
plt.figure(figsize=(12, 6))
sns.histplot(df['FantasyPoints'], kde=True)
plt.title('Distribution of Fantasy Points')
plt.xlabel('Fantasy Points')
plt.show()

# Top players by Fantasy Points
top_players = df.groupby('Player')['FantasyPoints'].mean().sort_values(ascending=False).head(20)
plt.figure(figsize=(12, 6))
top_players.plot(kind='bar')
plt.title('Top 20 Players by Average Fantasy Points')
plt.xlabel('Player')
plt.ylabel('Average Fantasy Points')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Positional analysis
df['Position'] = df['Player'].apply(lambda x: x.split()[-1])
position_stats = df.groupby('Position')['FantasyPoints'].describe()
print(position_stats)

plt.figure(figsize=(10, 6))
sns.boxplot(x='Position', y='FantasyPoints', data=df)
plt.title('Fantasy Points Distribution by Position')
plt.show()

# Year-over-year trends
yearly_avg = df.groupby('Year')['FantasyPoints'].mean()
plt.figure(figsize=(10, 6))
yearly_avg.plot(kind='line', marker='o')
plt.title('Average Fantasy Points per Year')
plt.xlabel('Year')
plt.ylabel('Average Fantasy Points')
plt.show()
```

This notebook provides a starting point for exploring the data, including correlations between statistics, distributions of fantasy points, top performers, positional analysis, and year-over-year trends.

