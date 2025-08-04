import json

in_path = ("jobs_v2.json")
with open(in_path, "r") as f:
    jobs = json.load(f)

for job in jobs:
    if job.l