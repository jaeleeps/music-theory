import sys, json, importlib.util
spec = importlib.util.spec_from_file_location("r", sys.argv[1]); r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
key = {}
for k in "ABCD":
    _, parts = r.parse(r.load_root(f"{sys.argv[2]}/{k}.musicxml"))
    notes = []
    for pi, p in enumerate(parts):
        for e in p["events"]:
            if e["pitch"] is None or e["grace"]:
                continue
            staff = e["staff"] if len(parts) == 1 else pi + 1
            notes.append([int(e["measure"]), staff, str(e["onset"]), e["pitch"], str(e["dur"])])
    key[k] = notes
    print(k, len(notes), "notes; measures", sorted({n[0] for n in notes}), "staves", sorted({n[1] for n in notes}))
json.dump(key, open(sys.argv[3], "w"))
