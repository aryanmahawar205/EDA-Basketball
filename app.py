import streamlit as st
import pandas as pd
import base64 # to encode the data to be downloadable
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('NBA Player Stats Explorer')

st.markdown("""
This app performs simple webscraping of NBA player stats data!
* **Data source:** [Basketball Reference](https://www.basketball-reference.com/).
""")

# sidebar for user input from years 1950 to 2024
st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2025))))

# web scraping of NBA player stats
@st.cache_data # caches the data of loading fucntion to speed up the app
# function scrapes the NBA player stats for the selected year from Basketball Reference
# it then cleans the data and returns it as a DataFrame
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html" # constructing the URL for a particular selected year
    html = pd.read_html(url, header = 0) # reads all HTML tables found at the specified URL and return a list of DataFrames, while the 'header=0' argument specifies that the first row of the table contains the conlumn headers
    df = html[0] # extract the first DataFrame which contains the NBA player stats.
    raw = df.drop(df[df.Age == 'Age'].index) # deletes repeating headers in content
    raw = raw.fillna(0) # handling missing values (NaN) in the DataFrame by filling them to 0
    playerstats = raw.drop(['Rk'], axis=1) # dropping unnecessary columns like the 'Rk' column which likely contains ranking numbers as it is not needed for the analysis
    return playerstats # playerstatistics is the cleaned DataFrame which is returned from the function
playerstats = load_data(selected_year)

# sidebar - team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# sidebar - position selection
unique_pos = ['C','PF','SF','PG','SG'] # list of possible player positions: Center (C), Power Forward (PF), Small Forward (SF), Point Guard (PG), and Shooting Guard (SG)
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# filtering data by including only the rows where the team ('Tm') and position ('Pos') match the user's selections
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# download filtered data as CSV
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# heatmap of intercorrelation matrix
if st.button('Intercorrelation Heatmap'):
    try:
        st.header('Intercorrelation Matrix Heatmap')
        
        # Assuming df_selected_team is already defined in your code
        if 'df_selected_team' not in globals():
            st.error("Dataframe 'df_selected_team' is not defined.")
        else:
            df_selected_team.to_csv('output.csv', index=False)
            df = pd.read_csv('output.csv')

            # Select only numeric columns for correlation matrix
            df_numeric = df.select_dtypes(include=[np.number])

            if df_numeric.empty:
                st.error("No numeric columns available for correlation.")
            else:
                corr = df_numeric.corr()
                mask = np.zeros_like(corr)
                mask[np.triu_indices_from(mask)] = True
                
                with sns.axes_style("white"):
                    f, ax = plt.subplots(figsize=(10, 8))
                    sns.heatmap(
                        corr,
                        mask=mask,
                        vmax=1,
                        square=True,
                        annot=True,
                        cmap="coolwarm",
                        cbar_kws={"shrink": .8},
                        ax=ax,
                        annot_kws={"size": 6},  # Even smaller font size for annotations
                    )
                    
                    # Adjusting the font size for axis labels and title
                    ax.set_xlabel('Variables', fontsize=8)
                    ax.set_ylabel('Variables', fontsize=8)
                    ax.set_title('Correlation Matrix Heatmap', fontsize=10)

                st.pyplot(f)
    except Exception as e:
        st.error(f"An error occurred: {e}")
