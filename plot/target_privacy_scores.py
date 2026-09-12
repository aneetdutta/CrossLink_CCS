import pandas as pd

file_a = ""   # CSV that you want to select user_id FROM
file_b = "largest_A_ids.csv"   # CSV that contains the reference user_id column
out_file = "matched_user_ids_baseline.csv"

a = pd.read_csv(file_a, usecols=["user_id","privacy_score"], dtype={"user_id": "string"})
b = pd.read_csv(file_b, usecols=["user_id"], dtype={"user_id": "string"})

a["user_id"] = a["user_id"].str.strip()
b["user_id"] = b["user_id"].str.strip()

matched = (
    a.merge(b, on="user_id", how="inner")  # brings privacy_score from B
     .dropna(subset=["user_id"])
     .drop_duplicates(subset=["user_id"])
     .reset_index(drop=True)
)

matched.to_csv(out_file, index=False)
print(f"Saved {len(matched)} matched rows (user_id + privacy_score) to: {out_file}")
