from glob import glob
import os

folder = glob("sess/*/*")
x = 15
for i in folder:
    y = i.split("\\")[-1]
    with open(f"sessionses/{y.replace('.session', '').strip()}.json", "w") as f:
        js = {"session_file": y.replace(".session", "").strip(), "phone": y.replace("+", "").replace(".session", "").strip()}
        f.write(str(js))
    os.rename(i, f"sessionses/{y}")
    if x > 15:
        print("done")
        break
