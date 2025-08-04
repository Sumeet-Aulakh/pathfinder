import json

from pathfinder import pathfinder
from pathfinder import llm_json
from prompts import EMAIL_COVER_LETTER_PROMPT
from rich import print


# in_path = "jobs_v2.json"
in_path = "job.json"
with open(in_path, 'r') as f:
    jobs = json.load(f)

i = 0


def generate_email(resume, cover_letter, job_description):
    result = llm_json(EMAIL_COVER_LETTER_PROMPT.format(resume_data=resume, cover_letter_data=cover_letter, job_description_data=job_description))
    # print(result)
    email_in_path = "email.txt"
    with open(email_in_path, 'w') as f:
        f.write(result["email_body"])

while i < len(jobs):
    job = jobs[i]
    try:
        resume_json, cover_letter_json = pathfinder(job["job_description"])
        print(job["apply"])
        if "by email" in str(job["apply"]).lower():
            print("[bold green]Generating email...[/bold green]")
            generate_email(resume=resume_json, cover_letter=cover_letter_json, job_description=job["job_description"])
            print("How to apply?")
            print(job["apply"])
        answer = input("Press y to continue...")
        if answer =="y":
            i+=1
            continue
        else:
            break
    except Exception as e:
        print("Error while generating email or using pathfinder:", e)
        raise e

