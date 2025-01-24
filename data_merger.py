import pandas as pd
import numpy as np
Input_data_path = "Track Chart csvs/"
grades = pd.read_csv(Input_data_path + "bnsf-grades-all.csv")
curves = pd.read_csv(Input_data_path + "bnsf-curves-all.csv")
speed = pd.read_csv(Input_data_path + "bnsf-speed-all.csv")
grades["LINE_SEGMENT"] = grades["LINE_SEGMENT"].str.replace(',', '')
grades["LINE_SEGMENT"] = grades["LINE_SEGMENT"].astype(float)
curves["LINE_SEGMENT"] = curves["LINE_SEGMENT"].str.replace(',', '')
curves["LINE_SEGMENT"] = curves["LINE_SEGMENT"].astype(float)
line_segment_number = 1
grade_line = grades[grades["LINE_SEGMENT"]==line_segment_number]
grade_line = grade_line[["LINE_SEGMENT","BEG MP","GRADE_TO_NEXT"]]
print(grade_line)
grade_end_mp = []
curve_line = curves[curves["LINE_SEGMENT"]==line_segment_number]
curve_line = curve_line[["LINE_SEGMENT","BEG MP","END MP","LENGTH (FT)","CURVE NUMBER","DIRECTION","DEG OF CURVE"]]
speed_line = speed[speed["LINE_SEGMENT"]==line_segment_number]
speed_line = speed_line.drop_duplicates()
speed_line =speed_line.reset_index()
speed_line_speed = speed_line[["FREIGHT SPEED"]]
speed_line = speed_line[["LINE_SEGMENT","BEG MP","END MP"]]
for i in range(len(grade_line)-1):
    grade_end_mp.append(grade_line.loc[i+1,"BEG MP"])
grade_end_mp.append(speed_line.loc[len(speed_line)-1,"END MP"])
grade_speed = np.zeros(len(grade_line))
grade_curve_length = np.zeros(len(grade_line))
grade_curve_number = np.zeros(len(grade_line))
grade_curve_direction = np.zeros(len(grade_line))
grade_degree_of_curve = np.zeros(len(grade_line))
grade_line.insert(loc=2, column='END MP', value=grade_end_mp)
grade_line.insert(loc=3, column='SPEED', value=grade_speed)
grade_line.insert(loc=4, column='LENGTH (FT)', value=grade_curve_length)
grade_line.insert(loc=5, column='CURVE NUMBER', value=grade_curve_number)
grade_line.insert(loc=6, column='DIRECTION', value=grade_curve_direction)
grade_line.insert(loc=7, column='DEG OF CURVE', value=grade_degree_of_curve)
curve_grade = np.zeros(len(curve_line))
curve_speed = np.zeros(len(curve_line))
curve_line.insert(loc=3, column='SPEED', value=curve_speed)
curve_line.insert(loc=8, column='GRADE_TO_NEXT', value=curve_grade)
speed_curve_length = np.zeros(len(speed_line))
speed_curve_number = np.zeros(len(speed_line))
speed_curve_direction = np.zeros(len(speed_line))
speed_degree_of_curve = np.zeros(len(speed_line))
speed_grade = np.zeros(len(speed_line))
speed_line.insert(loc=3,column='SPEED', value=speed_line_speed)
speed_line.insert(loc=4, column='LENGTH (FT)', value=speed_curve_length)
speed_line.insert(loc=5, column='CURVE NUMBER', value=speed_curve_number)
speed_line.insert(loc=6, column='DIRECTION', value=speed_curve_direction)
speed_line.insert(loc=7, column='DEG OF CURVE', value=speed_degree_of_curve)
speed_line.insert(loc=8, column='GRADE_TO_NEXT', value=speed_grade)
consolidate = pd.concat([grade_line, curve_line, speed_line])
consolidate = consolidate.sort_values(['BEG MP', 'END MP'], ascending=[True, True])
consolidate =consolidate.reset_index()
consolidate=consolidate.drop(['index'], axis=1)
print(consolidate)