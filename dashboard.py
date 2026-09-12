import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Immune Cell Population Analysis", layout="wide")

DB_PATH = 'cell_count.db'

@st.cache_data
def load_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

st.title("Teiko Take-Home: Immune Cell Population Analysis")

tab1, tab2, tab3 = st.tabs(["Part 2: Relative Frequencies", "Part 3: Boxplot", "Part 4: Significance Results"])

with tab1:
    st.header("Cell Population Relative Frequencies")
    freq_df = load_table("population_relative_frequencies")
    st.dataframe(freq_df, use_container_width=True)


with tab2:
    st.header("Population Relative Frequencies by Response to Miraclib Treatment")

    df_part3 = load_table("miraclib_response_comparison")


    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='population', y='percentage', hue='response', data=df_part3, ax=ax)
    ax.set_title('Population Relative Frequencies by Response to Miraclib Treatment')
    ax.set_xlabel('Immune Cell Population')
    ax.set_ylabel('Relative Frequency (%)')

    st.pyplot(fig)
    plt.close(fig)


with tab3:
    st.header("Statistical Significance: Responders vs Non-Responders")
    results_df = load_table("melanoma_baseline_summary")
    st.dataframe(results_df, use_container_width=True)