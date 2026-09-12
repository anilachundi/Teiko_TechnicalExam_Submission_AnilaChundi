import sqlite3
import pandas as pd

'''
PART1: pull data from csv file and load it into a pandas dataframe
'''

df = pd.read_csv('data/cell-count.csv')
#print(df.head())


connection = sqlite3.connect('cell_count.db')
cursor = connection.cursor()


#Drop Table if it already exists
cursor.execute("DROP TABLE IF EXISTS cell_counts")
cursor.execute("DROP TABLE IF EXISTS samples")
cursor.execute("DROP TABLE IF EXISTS patients")
cursor.execute("DROP TABLE IF EXISTS projects")


try:  
    cursor.execute(""" CREATE TABLE projects (project VARCHAR(50) PRIMARY KEY) """)
    cursor.execute(""" CREATE TABLE patients (subject VARCHAR(50) PRIMARY KEY,  project VARCHAR(50), condition TEXT, age INTEGER, sex TEXT, treatment TEXT, response TEXT, FOREIGN KEY (project) REFERENCES projects(project) ) """)
    cursor.execute(""" CREATE TABLE samples (sample VARCHAR(50) PRIMARY KEY, subject VARCHAR(50), sample_type TEXT, time_from_treatment INTEGER, FOREIGN KEY (subject) REFERENCES patients(subject)) """)

    cursor.execute(""" CREATE TABLE cell_counts (sample VARCHAR(50), b_cell INTEGER, cd8_t_cell INTEGER, cd4_t_cell INTEGER, \
        nk_cell INTEGER, monocyte INTEGER, FOREIGN KEY (sample) REFERENCES samples(sample)) """)

    connection.commit()
except sqlite3.Error as e:
    print(f"An error occurred: {e}")

#Write the data from the DataFrame to the SQLite database
projects_df = df[['project']].drop_duplicates()
projects_df.to_sql('projects', connection, if_exists='append', index=False)

patients_df = df[['subject', 'project', 'condition', 'age', 'sex', 'treatment', 'response']].drop_duplicates(subset='subject')
patients_df.to_sql('patients', connection, if_exists='append', index=False)

samples_df = df[['sample', 'subject', 'sample_type', 'time_from_treatment_start']].drop_duplicates(subset='sample')
samples_df = samples_df.rename(columns={'time_from_treatment_start': 'time_from_treatment'})  # match your schema's column name
samples_df.to_sql('samples', connection, if_exists='append', index=False)

cell_counts_df = df[['sample', 'b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']]
cell_counts_df.to_sql('cell_counts', connection, if_exists='append', index=False)

connection.commit()

'''
PART 2: Calculate the frequency of each cell type for each sample and display a relative frequency summary table
'''

df_part2 = pd.read_sql_query("SELECT * FROM cell_counts", connection)
populations_columns = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
df_part2['total_count'] = df_part2[populations_columns].sum(axis=1)

df_part2 = df_part2.melt(id_vars=['sample', 'total_count'], value_vars=populations_columns, var_name='population', value_name='count')
df_part2['percentage'] = (df_part2['count'] / df_part2['total_count']) * 100
df_part2.to_sql('population_relative_frequencies', connection, if_exists='replace', index=False)

'''
PART 3: Compare the relative frequencies of immune cell populations between responders and non-responders to miraclib treatment in melanoma patients using boxplots
'''
query = """
SELECT cc.sample, cc.population, cc.percentage, p.response, s.sample_type, p.condition, p.treatment
FROM population_relative_frequencies cc
JOIN samples s on cc.sample = s.sample
JOIN patients p on s.subject = p.subject
WHERE p.treatment = 'miraclib' AND p.condition = 'melanoma' AND s.sample_type = 'PBMC'
"""
df_part3 = pd.read_sql_query(query, connection)
df_part3.to_sql('miraclib_response_comparison', connection, if_exists='replace', index=False)
# print(df_part3.response.value_counts())

#plot population relative frequencies
import seaborn as sns
import matplotlib.pyplot as plt
populations = df_part3['population'].unique()
sns.boxplot(x='population', y='percentage', hue='response', data=df_part3)
plt.title('Population Relative Frequencies by Response to Miraclib Treatment')
plt.xlabel('Immune Cell Population')
plt.ylabel('Relative Frequency (%)')    
plt.show()

'''
PART 4: Find all melanoma patients at baseline (time_from_treatment = 0), treatment = miraclib, then get # samples from each project, # subjects who respond with yes vs no, and male vs female
'''

query = """
SELECT p.project, COUNT(DISTINCT s.sample) AS num_samples,
       COUNT(DISTINCT p.subject) AS num_subjects,
       SUM(CASE WHEN p.response = 'yes' THEN 1 ELSE 0 END) AS num_responders,
       SUM(CASE WHEN p.response = 'no' THEN 1 ELSE 0 END) AS num_non_responders,
       SUM(CASE WHEN p.sex = 'M' THEN 1 ELSE 0 END) AS num_males,
       SUM(CASE WHEN p.sex = 'F' THEN 1 ELSE 0 END) AS num_females
    FROM patients p
    JOIN samples s ON p.subject = s.subject
    WHERE p.condition = 'melanoma' AND p.treatment = 'miraclib' AND s.time_from_treatment = 0
    GROUP BY p.project"""
df_part4 = pd.read_sql_query(query, connection)
# print(df_part4)
df_part4.to_sql('melanoma_baseline_summary', connection, if_exists='replace', index=False)

""" Answer Last Question: Avg # b_cell counts for melanoma males who respond yes, at time = 0, across all treatments and sample types"""
query = """
SELECT AVG(cc.b_cell) AS avg_b_cell_count 
FROM cell_counts cc
JOIN samples s on cc.sample = s.sample
JOIN patients p on s.subject = p.subject
WHERE p.condition = 'melanoma' AND p.sex = 'M' AND p.response = 'yes' AND s.time_from_treatment = 0
"""
df_avg_b_cell = pd.read_sql_query(query, connection)
# print(df_avg_b_cell)

connection.close()