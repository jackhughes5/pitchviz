import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import statcast_pitcher, playerid_lookup
import pandas as pd

# --- CONFIGURATION ---
PLAYER_LAST = "Skubal"
PLAYER_FIRST = "Tarik"
START_DATE = "2024-03-28"
END_DATE = "2024-10-01"

def get_pitcher_data(last, first, start, end):
    #Lookup Player ID
    player_ids = playerid_lookup(last, first)
    
    if player_ids.empty:
        print("Player not found!")
        return None
    
    #Grab the MLBAM ID (the ID Statcast uses)
    player_id = player_ids['key_mlbam'].iloc[0]
    print(f"Found ID for {first} {last}: {player_id}")
    
    #Fetch Statcast Data
    print(f"Fetching data from {start} to {end}...")
    df = statcast_pitcher(start, end, player_id)
    
    return df

def plot_arsenal(df, player_name):
    sns.set_theme(style="whitegrid")
    
    # Create a figure with 3 subplots side-by-side
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # --- PLOT 1: MOVEMENT PROFILE ---
    sns.scatterplot(
        data=df, 
        x='pfx_x', 
        y='pfx_z', 
        hue='pitch_type', 
        palette='deep',
        alpha=0.7, 
        ax=axes[0]
    )
    axes[0].set_title(f"Movement Profile (Catcher's View)", fontsize=14)
    axes[0].set_xlabel("Horizontal Break (in)", fontsize=12)
    axes[0].set_ylabel("Vertical Break (in)", fontsize=12)
    axes[0].axhline(0, color='black', linewidth=1, linestyle='--')
    axes[0].axvline(0, color='black', linewidth=1, linestyle='--')
    axes[0].legend(loc='lower right', title='Pitch Type')

    # --- PLOT 2: VELOCITY DISTRIBUTION ---
    sns.kdeplot(
        data=df, 
        x='release_speed', 
        hue='pitch_type', 
        fill=True, 
        palette='deep', 
        warn_singular=False,
        ax=axes[1]
    )
    axes[1].set_title(f"Velocity Distribution", fontsize=14)
    axes[1].set_xlabel("Velocity (MPH)", fontsize=12)
    axes[1].get_legend().remove() # Remove duplicate legend to save space

    # --- PLOT 3: "STUFF" (Spin Rate vs. Velocity) ---
    sns.scatterplot(
        data=df,
        x='release_speed',
        y='release_spin_rate',
        hue='pitch_type',
        palette='deep',
        alpha=0.6,
        ax=axes[2]
    )
    axes[2].set_title(f"Spin vs. Velocity", fontsize=14)
    axes[2].set_xlabel("Velocity (MPH)", fontsize=12)
    axes[2].set_ylabel("Spin Rate (RPM)", fontsize=12)
    axes[2].legend(loc='upper left', title='Pitch Type')

    fig.suptitle(f"{player_name} - 2024 Arsenal Analysis", fontsize=20, fontweight='bold', y=1.05)

    plt.tight_layout()
    

    filename = f"{player_name.replace(' ', '_')}_Arsenal.png"
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    print(f"Success! Graph saved as {filename}")
    
    plt.show()

if __name__ == "__main__":
    df = get_pitcher_data(PLAYER_LAST, PLAYER_FIRST, START_DATE, END_DATE)
    
    if df is not None and not df.empty:
        print(f"Data loaded: {len(df)} pitches found.")
        
        df_clean = df.dropna(subset=['pitch_type', 'pfx_x', 'pfx_z', 'release_speed'])
        
        plot_arsenal(df_clean, f"{PLAYER_FIRST} {PLAYER_LAST}")
    else:
        print("No data found or error in fetching.")