import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import regex as re
Input_data_path = "Processed csvs/"
Output_data_path = "Crew Districts/"
Master_listing = pd.read_csv("BNSF Crew Districts.csv")
Master_listing = pd.read_excel("BNSF-segments-JP.xlsx")
Master_listing = pd.read_excel("BNSF-segments-Truman.xlsx")
print(Master_listing)
Master_listing['Begin MP 1'] = pd.to_numeric(Master_listing['Begin MP 1'], errors='coerce')
Master_listing['Begin MP 2'] = pd.to_numeric(Master_listing['Begin MP 2'], errors='coerce')
Master_listing['Begin MP 3'] = pd.to_numeric(Master_listing['Begin MP 3'], errors='coerce')
Master_listing['Begin MP 4'] = pd.to_numeric(Master_listing['Begin MP 4'], errors='coerce')
Master_listing['Begin MP 5'] = pd.to_numeric(Master_listing['Begin MP 5'], errors='coerce')
Master_listing['End MP 1'] = pd.to_numeric(Master_listing['End MP 1'], errors='coerce')
Master_listing['End MP 2'] = pd.to_numeric(Master_listing['End MP 2'], errors='coerce')
Master_listing['End MP 3'] = pd.to_numeric(Master_listing['End MP 3'], errors='coerce')
Master_listing['End MP 4'] = pd.to_numeric(Master_listing['End MP 4'], errors='coerce')
Master_listing['End MP 5'] = pd.to_numeric(Master_listing['End MP 5'], errors='coerce')
for i in range(len(Master_listing)):
    print("Start processing line " + str(i))
    Output = pd.DataFrame(np.zeros(shape=(0,9)),columns=["LINE_SEGMENT","BEG MP","END MP", "SPEED", "GRADE_TO_NEXT","DIRECTION", "DEG OF CURVE", "LENGTH (M)", "ELEV (M)"])
    subdivision_name = Master_listing.loc[i,"Start"] + " to " + Master_listing.loc[i,"End"]
    subdivision_name = re.sub(r'\s*,\s*', '_', subdivision_name.strip())
    column_name = "Subdivision "
    segment_list = [1,2,3,4,5]
    for segment_num in segment_list:
        Subdivision_column = column_name + str(segment_num)
        line_segment_num = "Segment " + str(segment_num)
        if isinstance(Master_listing.loc[i,Subdivision_column],str):
            line_segment_file_num = int(Master_listing.loc[i,line_segment_num])
            Begin_MP_name = "Begin MP " + str(segment_num)
            End_MP_name = "End MP " + str(segment_num)
            Begin_MP = Master_listing.loc[i,Begin_MP_name]
            End_MP = Master_listing.loc[i,End_MP_name]
            if Master_listing.loc[i,Begin_MP_name] < Master_listing.loc[i,End_MP_name]:
                line_segment_file_name = "line segment " + str(line_segment_file_num) + ".0.csv"
                line_segment_file = pd.read_csv(Input_data_path + line_segment_file_name)
                line_segment_file = line_segment_file[line_segment_file["BEG MP"] >= Begin_MP]
                line_segment_file = line_segment_file[line_segment_file["END MP"] <= End_MP]
            else:
                line_segment_file_name = "line segment " + str(line_segment_file_num) + ".0 reversed.csv"
                line_segment_file = pd.read_csv(Input_data_path + line_segment_file_name)
                line_segment_file = line_segment_file[line_segment_file["BEG MP"] <= Begin_MP]
                line_segment_file = line_segment_file[line_segment_file["END MP"] >= End_MP]
            Output = pd.concat([Output, line_segment_file])
            Output = Output[["LINE_SEGMENT","BEG MP","END MP", "SPEED", "GRADE_TO_NEXT","DIRECTION", "DEG OF CURVE", "LENGTH (M)", "ELEV (M)"]]
            Output = Output.reset_index()
    Output = Output[["LINE_SEGMENT","BEG MP","END MP", "SPEED", "GRADE_TO_NEXT","DIRECTION", "DEG OF CURVE", "LENGTH (M)", "ELEV (M)"]]
    Output.to_csv(Output_data_path + subdivision_name + ".csv")
    print("Finish processing line " + str(i) +
          "crew district name: " + subdivision_name)