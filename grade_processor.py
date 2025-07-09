import pandas as pd
import numpy as np

mile_to_meter = 1609.34
Input_data_path = "Track Chart csvs/"
grades = pd.read_csv(Input_data_path + "bnsf-grades-all-cleaned.csv")
tracker = 0
for i in range (len(grades)):
    if abs(grades.loc[i,"GRADE_TO_NEXT"]) > 4:
        init_value = grades.loc[i,"GRADE_TO_NEXT"]
        grades.loc[i,"GRADE_TO_NEXT"] = 1/2 * (grades.loc[i-1,"GRADE_TO_NEXT"] + grades.loc[i+1,"GRADE_TO_NEXT"])
        tracker += 1
        after_value = grades.loc[i,"GRADE_TO_NEXT"]
        print("Irregular grade #" + str(tracker) + " spotted, value = " + str(init_value))
        print("Adjusted to: " + str(after_value))
grades.to_csv(Input_data_path + "bnsf-grades-all-cleaned.csv")