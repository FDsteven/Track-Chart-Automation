import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
mile_to_meter = 1609.34
Input_data_path = "Track Chart csvs/"
grades = pd.read_csv(Input_data_path + "bnsf-grades-all.csv")
grades["LINE_SEGMENT"] = grades["LINE_SEGMENT"].str.replace(',', '')
grades["LINE_SEGMENT"] = grades["LINE_SEGMENT"].astype(float)
line_segments = grades["LINE_SEGMENT"].unique()
for line_segment in line_segments:
    line_segment_name = str(line_segment)
    input_file_name = "line segment " + line_segment_name + ".csv"
    output_file_name = "line segment " + line_segment_name + " reversed.csv"
    original = pd.read_csv(input_file_name)
    print(original)
    reverse_grade = np.zeros(len(original))
    reverse_curve_direction = np.zeros(len(original))
    MP_BEG = np.zeros(len(original))
    MP_END = np.zeros(len(original))
    reverse_segment = original[["LINE_SEGMENT","BEG MP","END MP","SPEED","GRADE_TO_NEXT","DIRECTION","DEG OF CURVE","LENGTH (M)","ELEV (M)"]]

    for i in range(len(original)):
        reverse_segment.loc[i,"END MP"] = original.loc[i,"BEG MP"]
        reverse_segment.loc[i,"BEG MP"] = original.loc[i,"END MP"]
        reverse_segment.loc[i,"GRADE_TO_NEXT"] = original.loc[i,"GRADE_TO_NEXT"]*(-1)
        if original.loc[i,"DIRECTION"] == "R":
            reverse_segment.loc[i,"DIRECTION"] = "L"
        if original.loc[i,"DIRECTION"] == "L":
            reverse_segment.loc[i,"DIRECTION"] = "R"
    reverse_segment = reverse_segment[::-1].reset_index(drop=True)
    print(line_segment_name + " Done")
    reverse_segment.to_csv(output_file_name)