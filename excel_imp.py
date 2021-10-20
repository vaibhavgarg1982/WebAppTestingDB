'''database schema
        database name testing.db
        tables
        1. Mst_testcases (testcase_id, name, test category, description, steps, expected_result, automated)
        2. Mst_projects (project_id, name, description)
        3. Mapping (map_id, project_id, testcase_id)
        4. testresults(tr_id, map_id, result_description, config_info, tester, execution_date, pass_fail)
        ON DELETE CASCADE
        
'''

# import data from excel file to Mst_testcases table. Excel file has the columns: 
# name, test_category, description, steps, expected_result, automated
# the data needs to be appended to existing data.
# respect the primary key constraint. Primary key is testcase_id. auto increment.

import pandas as pd
import sqlite3
conn = sqlite3.connect("testing.db")
# enforce foreign key rules
conn.execute("PRAGMA foreign_keys = 1")
c = conn.cursor()
# read excel file, forst row is the header
df = pd.read_excel("testcases.xlsx", header=1)
df.drop(df.columns[0], axis=1, inplace=True)
df.to_sql("Mst_testcases", conn, if_exists="append", index=False)
