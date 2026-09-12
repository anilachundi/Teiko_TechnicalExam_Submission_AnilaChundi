import sqlite3
import pandas as pd

'''
pull data from csv file and load it into a pandas dataframe
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


    cursor.execute(""" CREATE TABLE cell_counts (sample VARCHAR(50), b_cell INTEGER, cd8_t_cell INTEGER, cd4_t_cell INTEGER \
        nk_cell INTEGER, monocyte INTEGER, FOREIGN KEY (sample) REFERENCES samples(sample)) """)

    connection.commit()
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if connection:
        connection.close()
