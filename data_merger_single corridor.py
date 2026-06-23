import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

mile_to_meter = 1609.34
def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row])]
           ).reset_index(drop=True)
constant_speed = 40 #mph
corridor_name = "CapMetro Alignment"
grades = pd.read_csv(corridor_name + " grades.csv")
curves = pd.read_csv(corridor_name + " curves.csv")
# speed = pd.read_csv(Input_data_path + "bnsf-speed-all.csv")
# grades["LINE_SEGMENT"] = grades["LINE_SEGMENT"].str.replace(',', '')

grade_line = grades[["BEG MP","END MP","LENGTH (FT)","GRADE_TO_NEXT"]]
# print(grade_line)
curve_line = curves[["BEG MP","END MP","LENGTH (FT)","Curvature (degrees)"]]

from typing import Sequence

def consolidate_geometry(
    grade_df: pd.DataFrame,
    curv_df: pd.DataFrame,
    *,
    beg_col="BEG MP",
    end_col="END MP",
    grade_cols: Sequence[str] = (),
    curv_cols: Sequence[str] = (),
    closed="left",
    fill_missing=None
) -> pd.DataFrame:
    g = grade_df.copy()
    c = curv_df.copy()

    def sanitize(df: pd.DataFrame) -> pd.DataFrame:
        df[beg_col] = pd.to_numeric(df[beg_col], errors="coerce")
        df[end_col] = pd.to_numeric(df[end_col], errors="coerce")
        df = df.dropna(subset=[beg_col, end_col])
        swap_mask = df[beg_col] > df[end_col]
        if swap_mask.any():
            b = df.loc[swap_mask, beg_col].to_numpy()
            e = df.loc[swap_mask, end_col].to_numpy()
            df.loc[swap_mask, beg_col] = e
            df.loc[swap_mask, end_col] = b
        df = df[df[end_col] > df[beg_col]]
        df = df.sort_values([beg_col, end_col]).reset_index(drop=True)
        return df

    if not g.empty: g = sanitize(g)
    if not c.empty: c = sanitize(c)

    parts = []
    if not g.empty:
        parts.append(g[[beg_col, end_col]].to_numpy().ravel())
    if not c.empty:
        parts.append(c[[beg_col, end_col]].to_numpy().ravel())
    if not parts:
        return pd.DataFrame(columns=[beg_col, end_col, *grade_cols, *curv_cols])

    breakpoints = np.unique(np.concatenate(parts))
    if breakpoints.size < 2:
        return pd.DataFrame(columns=[beg_col, end_col, *grade_cols, *curv_cols])

    consolidated = pd.DataFrame({
        beg_col: breakpoints[:-1],
        end_col: breakpoints[1:]
    })

    for col in grade_cols:
        consolidated[col] = np.nan
    for col in curv_cols:
        consolidated[col] = np.nan

    def paint(src: pd.DataFrame, value_cols: Sequence[str]):
        if src.empty or not value_cols:
            return
        for _, row in src.iterrows():
            b = row[beg_col]
            e = row[end_col]
            if not (e > b):
                continue
            li = np.searchsorted(breakpoints, b, side="left")
            ri = np.searchsorted(breakpoints, e, side="left")
            if ri <= li:
                continue
            for col in value_cols:
                consolidated.loc[li:ri-1, col] = row[col]

    paint(g, grade_cols)
    paint(c, curv_cols)

    if isinstance(fill_missing, dict):
        for col, fill_val in fill_missing.items():
            if col in consolidated.columns:
                consolidated[col] = consolidated[col].fillna(fill_val)

    info_cols = list(grade_cols) + list(curv_cols)
    if info_cols:
        consolidated = consolidated.loc[~consolidated[info_cols].isna().all(axis=1)].reset_index(drop=True)

    return consolidated

# Read files again
grades_df = grade_line
curves_df = curve_line

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {c: c.strip() for c in df.columns}
    df = df.rename(columns=mapping)
    candidates_beg = ["BEG MP", "BEG_MP", "BEGIN MP", "BEGIN_MP", "START MP", "START_MP", "MP BEG", "MP_BEG"]
    candidates_end = ["END MP", "END_MP", "FINISH MP", "FINISH_MP", "MP END", "MP_END", "STOP MP", "STOP_MP"]
    def first_present(cands, cols):
        for k in cands:
            if k in cols:
                return k
        return None
    beg_actual = first_present(candidates_beg, df.columns) or ("BEG MP" if "BEG MP" in df.columns else None)
    end_actual = first_present(candidates_end, df.columns) or ("END MP" if "END MP" in df.columns else None)
    if "BEG MP" not in df.columns and beg_actual:
        df = df.rename(columns={beg_actual: "BEG MP"})
    if "END MP" not in df.columns and end_actual:
        df = df.rename(columns={end_actual: "END MP"})
    return df

grades_df = normalize_columns(grades_df)
curves_df = normalize_columns(curves_df)

grade_value_cols = [c for c in grades_df.columns if c not in ("BEG MP", "END MP")]
curv_value_cols = [c for c in curves_df.columns if c not in ("BEG MP", "END MP")]

consolidated_df = consolidate_geometry(
    grades_df,
    curves_df,
    beg_col="BEG MP",
    end_col="END MP",
    grade_cols=grade_value_cols,
    curv_cols=curv_value_cols,
    fill_missing={"GRADE_TO_NEXT":0.0,"Curvature (degrees)":0.0}
)
new_col = np.zeros(len(consolidated_df))
consolidated_df.insert(loc=4, column='SPEED', value=new_col)

consolidated_df["SPEED"] = constant_speed * 0.44704
for i in range(len(consolidated_df)):
    consolidated_df.loc[i,"LENGTH (FT)"] = 5280 * (consolidated_df.loc[i,"END MP"] - consolidated_df.loc[i,"BEG MP"])
for i in range(len(consolidated_df)):
    consolidated_df.loc[i,"LENGTH (M)"] = mile_to_meter * (consolidated_df.loc[i,"END MP"] - consolidated_df.loc[i,"BEG MP"])
new_data = consolidated_df.drop_duplicates(['BEG MP','END MP', 'GRADE_TO_NEXT'], keep='first')
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
print(new_data)
fig, ax = plt.subplots(3, 1, sharex=True)
ax[0].plot(
    np.array(new_data["END MP"]), 
    np.array(new_data["ELEV (M)"]),
    label="Track Elevation"
)
ax[0].set_ylabel('Elev (M)')
# ax[0].set_ylim([150, 850])
ax[0].legend()

# ax[-1].plot(
#     np.array(new_data["END MP"]), 
#     np.array(new_data["SPEED"]),
#     label='speed',
# )
# ax[-1].set_ylabel('speed')
# ax[-1].legend()
ax[1].plot(
    np.array(new_data["END MP"]), 
    np.array(new_data["Curvature (degrees)"]),
    label="Track Curvature"
)
ax[1].set_ylabel('Degree')
# ax[0].set_ylim([150, 850])
ax[1].legend()
ax[1].set_xlabel('MP')
ax[2].plot(
    np.array(new_data["END MP"]), 
    np.array(new_data["GRADE_TO_NEXT"]),
    label="Track Grade"
)
ax[2].set_ylabel('Grade')
# ax[0].set_ylim([150, 850])
ax[2].legend()
ax[2].set_xlabel('MP')
# plt.tight_layout()
plt.show()
new_data.to_csv("after_curve.csv")
consolidated_df.to_csv("after_speed.csv")
print("DONE")


print(consolidated_df)
consolidated_df.to_csv(corridor_name + " consolidated.csv", index=False)


# LEGACY CODE PENDING FIX
# speed_line = speed[speed["LINE_SEGMENT"]==line_segment_number]
# speed_line = speed_line.drop_duplicates()
# speed_line =speed_line.reset_index()
# speed_line_speed = speed_line[["FREIGHT SPEED"]]
# speed_line = speed_line[["LINE_SEGMENT","BEG MP","END MP"]]
# speed_line = speed_line.reset_index(drop=True)
curve_line = curve_line.reset_index(drop=True)
grade_line = grade_line.reset_index(drop=True)    
grade_curve_length = np.zeros(len(grade_line))
grade_curve_number = np.zeros(len(grade_line))
grade_curve_direction = np.zeros(len(grade_line))
grade_degree_of_curve = np.zeros(len(grade_line))
grade_line.insert(loc=4, column='Curvature (degrees)', value=grade_curve_number)

# print(grade_line)
curve_grade = np.zeros(len(curve_line))
curve_speed = np.zeros(len(curve_line))
curve_line.insert(loc=4, column='SPEED', value=curve_speed)
curve_line.insert(loc=5, column='GRADE_TO_NEXT', value=curve_grade)
consolidate = pd.concat([grade_line, curve_line])
consolidate = consolidate.sort_values(['BEG MP', 'END MP'], ascending=[True, True])
consolidate =consolidate.reset_index()
consolidate_copy = consolidate
consolidate_copy.to_csv("before_speed.csv")
# print(consolidate)
length = len(consolidate)
Speed_slice = consolidate["SPEED"]
consolidate["SPEED"] = constant_speed * 0.44704
length = len(consolidate) - 1
column_names = ["BEG MP","END MP","LENGTH (FT)","GRADE_TO_NEXT","Curvature (degrees)","SPEED"]
new_data = pd.DataFrame(columns=column_names)
for i in range(length):
    if consolidate.loc[i+1,"Curvature (degrees)"] != 0.0:
        if consolidate.loc[i+1,"BEG MP"] < consolidate.loc[i,"END MP"]:
            consolidate.loc[i+1,"GRADE_TO_NEXT"] = consolidate.loc[i,"GRADE_TO_NEXT"]


consolidate = consolidate.reset_index(drop=True)
# 
# new_data  = append_row(new_data , row_slice)
# Iterate through and find all curves and duplicate multiple same curves for different grades
length = len(consolidate)
for i in range(1,length):
    if (consolidate.loc[i,"BEG MP"] == 0.0):
        consolidate.loc[i,"BEG MP"] = consolidate.loc[0,"END MP"]
consolidate = consolidate.sort_values(['BEG MP', 'END MP'], ascending=[True, True])
consolidate = consolidate.reset_index()
for i in range(1,length):
    if consolidate.loc[i,"END MP"] == consolidate.loc[i+1,"BEG MP"]:
        row_slice = consolidate.loc[i,:]
    elif consolidate.loc[i,"END MP"] > consolidate.loc[i+1,"BEG MP"]:
        row_slice = consolidate.loc[i,:]
        row_slice[i,"END MP"] = consolidate.loc[i+1,"BEG MP"]
        new_data  = append_row(new_data , row_slice)
for i in range(length):
    if consolidate.loc[i,"Curvature (degrees)"] != 0.0:
        # print(i)
        count = 0
        for j in range(i + 1,length):
            if (consolidate.loc[j, "BEG MP"] <= consolidate.loc[i,"END MP"]) & (consolidate.loc[j,"Curvature (degrees)"] == 0.0):
                count += 1
            else:
                break
        if count < 1:
            row_slice = consolidate.loc[i,:]
            new_data  = append_row(new_data , row_slice)
            for s in range(i):
                if consolidate.loc[i-s,"Curvature (degrees)"] != 0.0:
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
plt.show()
new_data.to_csv("after_curve.csv")
consolidate.to_csv("after_speed.csv")
print("DONE")

