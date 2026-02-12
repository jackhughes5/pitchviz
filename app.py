import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import statcast_pitcher, playerid_lookup
import pandas as pd
from datetime import date

st.set_page_config(page_title="Pitcher Visualizer", layout="wide")

st.title("MLB Pitcher Arsenal Visualizer")
st.markdown("Use this tool to analyze the pitch movement and velocity of any MLB pitcher from any season.")

st.sidebar.header("Setup")
min_date = date(2000, 1, 1) 
max_date = date.today()

player_name_input = st.sidebar.text_input("Player Name", value="Tarik Skubal")

start_date = st.sidebar.date_input(
    "Start Date", 
    value=date(2025, 3, 28), 
    min_value=min_date, 
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "End Date", 
    value=date(2025, 10, 1), 
    min_value=min_date, 
    max_value=max_date
)

if start_date > end_date:
    st.sidebar.error("Error: End Date must be after Start Date.")
    st.stop()

@st.cache_data
def get_data(name, start, end):
    try:
        # Split name strictly for lookup (simple logic)
        first, last = name.split(" ")[0], name.split(" ")[1]
    except:
        return None, "Please enter a full name (First Last)."

    # Lookup ID
    player_ids = playerid_lookup(last, first)
    if player_ids.empty:
        return None, "Player not found. Check spelling."
    
    player_id = player_ids['key_mlbam'].iloc[0]
    
    # Fetch Data
    df = statcast_pitcher(str(start), str(end), player_id)
    return df, None

if st.sidebar.button("Analyze Pitcher"):
    with st.spinner(f"Fetching data for {player_name_input}..."):
        df, error = get_data(player_name_input, start_date, end_date)
    
    if df is not None and df.empty:
        st.warning(f"No data found for {player_name_input} between {start_date} and {end_date}. Try a different date range!")
        st.stop() 

    if error:
        st.error(error)
    elif df is None or df.empty:
        st.warning("No data found for this time period.")
    else:
        st.success(f"loaded {len(df)} pitches!")

        sns.set_theme(style="whitegrid")
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        
        # 1. Movement
        sns.scatterplot(data=df, x='pfx_x', y='pfx_z', hue='pitch_type', palette='deep', alpha=0.7, ax=axes[0])
        axes[0].set_title("Movement Profile (Catcher Perspective)")
        axes[0].axhline(0, color='black', ls='--')
        axes[0].axvline(0, color='black', ls='--')

        # 2. Velocity
        sns.kdeplot(data=df, x='release_speed', hue='pitch_type', fill=True, palette='deep', warn_singular=False, ax=axes[1])
        axes[1].set_title("Velocity Distribution")

        # 3. Spin vs Velo
        sns.scatterplot(data=df, x='release_speed', y='release_spin_rate', hue='pitch_type', palette='deep', alpha=0.6, ax=axes[2])
        axes[2].set_title("Spin vs. Velocity")
        
        plt.tight_layout()
        
        st.pyplot(fig)

        with st.expander("See Raw Data"):
            st.dataframe(df[['pitch_type', 'release_speed', 'pfx_x', 'pfx_z', 'release_spin_rate']].head(50))