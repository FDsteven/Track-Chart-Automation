import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

mile_to_meter = 1609.34
def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row])]
           ).reset_index(drop=True)
Input_data_path = "Track Chart csvs/"
grades = pd.read_csv(Input_data_path + "bnsf-grades-all.csv")
curves = pd.read_csv(Input_data_path + "bnsf-curves-all.csv")
speed = pd.read_csv(Input_data_path + "bnsf-speed-all.csv")
grades["LINE_SEGMENT"] = grades["LINE_SEGMENT"].str.replace(',', '')
grades["LINE_SEGMENT"] = grades["LINE_SEGMENT"].astype(float)
curves["LINE_SEGMENT"] = curves["LINE_SEGMENT"].str.replace(',', '')
curves["LINE_SEGMENT"] = curves["LINE_SEGMENT"].astype(float)
line_segment_number = 1
def line_segment_loader(num):
    line_segment_number = num
    grade_line = grades[grades["LINE_SEGMENT"]==line_segment_number]
    grade_line = grade_line[["LINE_SEGMENT","BEG MP","GRADE_TO_NEXT"]]
    # print(grade_line)
    grade_end_mp = []
    curve_line = curves[curves["LINE_SEGMENT"]==line_segment_number]
    curve_line = curve_line[["LINE_SEGMENT","BEG MP","END MP","LENGTH (FT)","CURVE NUMBER","DIRECTION","DEG OF CURVE"]]
    speed_line = speed[speed["LINE_SEGMENT"]==line_segment_number]
    speed_line = speed_line.drop_duplicates()
    speed_line =speed_line.reset_index()
    speed_line_speed = speed_line[["FREIGHT SPEED"]]
    speed_line = speed_line[["LINE_SEGMENT","BEG MP","END MP"]]
    speed_line = speed_line.reset_index(drop=True)
    curve_line = curve_line.reset_index(drop=True)
    grade_line = grade_line.reset_index(drop=True)    
    for i in range(len(grade_line)-1):
        grade_end_mp.append(grade_line.loc[i+1,"BEG MP"])
    if len(speed_line) >= 1:
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
        speed_line.insert(loc=9, column='SPEED_INDI', value="speed")
        grade_end_mp.append(speed_line.loc[len(speed_line)-1,"END MP"])
    else:
        grade_end_mp.append(grade_end_mp[-1] + 0.1)
        print("Fabricated Line Segment " + str(num) + " final MP")
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
    grade_line.insert(loc=9, column='SPEED_INDI', value="non_speed")
    # print(grade_line)
    curve_grade = np.zeros(len(curve_line))
    curve_speed = np.zeros(len(curve_line))
    curve_line.insert(loc=3, column='SPEED', value=curve_speed)
    curve_line.insert(loc=8, column='GRADE_TO_NEXT', value=curve_grade)
    curve_line.insert(loc=9, column='SPEED_INDI', value="non_speed")
    consolidate = pd.concat([grade_line, curve_line, speed_line])
    consolidate = consolidate.sort_values(['BEG MP', 'END MP', 'SPEED_INDI'], ascending=[True, True, True])
    consolidate =consolidate.reset_index()
    consolidate_copy = consolidate
    consolidate_copy.to_csv("before_speed.csv")
    # print(consolidate)
    length = len(consolidate)
    Speed_slice = consolidate["SPEED"]
    if len(speed_line) >= 1:
        if Speed_slice.sum() == 0:
            consolidate["SPEED"] = 10
        else:
            if consolidate.loc[0,"SPEED"] <= 0:
                speed_index = Speed_slice[Speed_slice != 0].index[0]
                consolidate.loc[0,"SPEED"] = consolidate.loc[speed_index,"SPEED"]
            for i in range(length):
                if consolidate.loc[i,"SPEED"] <= 0: 
                    speed_slice = Speed_slice[0:i+1]
                    speed_index = speed_slice[speed_slice != 0].index[-1]
                    consolidate.loc[i,"SPEED"] = consolidate.loc[speed_index,"SPEED"]
    else:
        consolidate["SPEED"] = 10
    length = len(consolidate) - 1
    column_names = ["LINE_SEGMENT","BEG MP","END MP","SPEED","LENGTH (FT)","CURVE NUMBER","DIRECTION","DEG OF CURVE","GRADE_TO_NEXT"]
    new_data = pd.DataFrame(columns=column_names)
    for i in range(length):
        if consolidate.loc[i+1,"CURVE NUMBER"] != 0.0:
            if consolidate.loc[i+1,"BEG MP"] < consolidate.loc[i,"END MP"]:
                consolidate.loc[i+1,"GRADE_TO_NEXT"] = consolidate.loc[i,"GRADE_TO_NEXT"]
    if consolidate.loc[0,"SPEED_INDI"] == "speed":
        consolidate.loc[0,"SPEED_INDI"] = "non_speed"
        consolidate.loc[0,"END MP"] = consolidate.loc[1,"BEG MP"]
    consolidate = consolidate[consolidate["SPEED_INDI"] == "non_speed"]
    consolidate = consolidate.reset_index(drop=True)
    # 
    # new_data  = append_row(new_data , row_slice)
    # Iterate through and find all curves and duplicate multiple same curves for different grades
    length = len(consolidate)
    for i in range(length):
        if consolidate.loc[i,"CURVE NUMBER"] != 0.0:
            # print(i)
            count = 0
            for j in range(i + 1,length):
                if (consolidate.loc[j, "BEG MP"] <= consolidate.loc[i,"END MP"]) & (consolidate.loc[j,"CURVE NUMBER"] == 0.0):
                    count += 1
                else:
                    break
            if count < 1:
                row_slice = consolidate.loc[i,:]
                new_data  = append_row(new_data , row_slice)
                for s in range(i):
                    if consolidate.loc[i-s,"CURVE NUMBER"] != 0.0:
                        row_slice = consolidate.loc[i-s,:]
                        row_slice.loc["BEG MP"] = consolidate.loc[i,"END MP"]
                        new_data  = append_row(new_data , row_slice)
                        break
            else:
                for j in range (count):
                    row_slice = consolidate.loc[i,:]
                    row_slice.loc["END MP"] = consolidate.loc[i + j + 1, "BEG MP"]
                    row_slice.loc["BEG MP"] = consolidate.loc[i + j, "BEG MP"]
                    row_slice.loc["GRADE_TO_NEXT"] = consolidate.loc[i + j, "GRADE_TO_NEXT"]
                    new_data  = append_row(new_data , row_slice)
                row_slice = consolidate.loc[i,:]
                if consolidate.loc[i + count, "BEG MP"] < row_slice.loc["END MP"]:
                    row_slice.loc["BEG MP"] = consolidate.loc[i + count, "BEG MP"]
                    row_slice.loc["GRADE_TO_NEXT"] = consolidate.loc[i + count, "GRADE_TO_NEXT"]
                    new_data  = append_row(new_data , row_slice)
                else:
                    break
        else:
            row_slice = consolidate.loc[i,:]
            new_data  = append_row(new_data , row_slice)
    # print(new_data)
    for i in range(len(new_data)):
        new_data.loc[i,"LENGTH (M)"] = mile_to_meter * (new_data.loc[i,"END MP"] - new_data.loc[i,"BEG MP"])
    new_data = new_data.drop_duplicates(['BEG MP','END MP','SPEED', 'GRADE_TO_NEXT'], keep='first')
    new_data = new_data[new_data["LENGTH (M)"] > 0]
    new_data = new_data.reset_index(drop=True)
    for i in range(len(new_data)-1):
        new_data.loc[i+1,"BEG MP"] = new_data.loc[i,"END MP"]
        new_data.loc[i,"LENGTH (M)"] = mile_to_meter * (new_data.loc[i,"END MP"] - new_data.loc[i,"BEG MP"])
    new_data = new_data[new_data["LENGTH (M)"] > 0]
    new_data = new_data.reset_index(drop=True)
    new_data.loc[0,"ELEV (M)"] = new_data.loc[0,"LENGTH (M)"] * new_data.loc[0,"GRADE_TO_NEXT"] / 100
    for i in range(len(new_data)-1):
        new_data.loc[i + 1,"ELEV (M)"] = new_data.loc[i,"ELEV (M)"] + new_data.loc[i + 1,"LENGTH (M)"] * new_data.loc[i + 1,"GRADE_TO_NEXT"] / 100
    # print(new_data)
    fig, ax = plt.subplots(4, 1, sharex=True)
    ax[0].plot(
        np.array(new_data["END MP"]), 
        np.array(new_data["ELEV (M)"]),
        label="Track Elevation"
    )
    ax[0].set_ylabel('Elev (M)')
    # ax[0].set_ylim([150, 850])
    ax[0].legend()

    ax[1].plot(
        np.array(new_data["END MP"]), 
        np.array(new_data["SPEED"]),
        label='speed',
    )
    ax[1].set_ylabel('speed')
    ax[1].legend()
    ax[2].plot(
        np.array(new_data["END MP"]), 
        np.array(new_data["DEG OF CURVE"]),
        label="Track Curvature"
    )
    ax[2].set_ylabel('Degree')
    # ax[0].set_ylim([150, 850])
    ax[2].legend()
    ax[2].set_xlabel('MP')
    ax[3].plot(
        np.array(new_data["END MP"]), 
        np.array(new_data["GRADE_TO_NEXT"]),
        label="Track Curvature"
    )
    ax[3].set_ylabel('Grade')
    # ax[0].set_ylim([150, 850])
    ax[3].legend()
    ax[3].set_xlabel('MP')
    # plt.tight_layout()
    # plt.show()
    new_data.to_csv("after_curve.csv")
    consolidate.to_csv("after_speed.csv")
    return new_data
line_segments = [1,2,3]
line_segments = grades["LINE_SEGMENT"].unique()
for line_segment in line_segments:
    if line_segment >= 424:
        line_segment_name = str(line_segment)
        print("Starting: ", line_segment_name)
        document_name = "line segment " + line_segment_name + ".csv"
        Line_segment_df = line_segment_loader(line_segment)
        print(line_segment_name + " Done")
        Line_segment_df.to_csv(document_name)
line_segments = grades["LINE_SEGMENT"].unique()
