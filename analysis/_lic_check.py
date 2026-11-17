import io, json, glob, os
for p in glob.glob(r"D:\projects\cyber-reverse\analysis\apdata-preserved-*\settings.json") + [r"C:\Users\wykk\AppData\Roaming\Cybersole\settings.json"]:
    d = json.loads(io.open(p, encoding='utf-8').read())
    lic = d.get("license")
    print(os.path.basename(os.path.dirname(p)), "| keys:", len(d), "| license:", (type(lic).__name__ if lic is not None else "absent"),
          "| bearer len:", len(d.get("bearer") or ""))
