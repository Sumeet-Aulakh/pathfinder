import os
import json
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from pymupdf import paper_size
from rich import print
from rich.prompt import Prompt
from markdown_pdf import MarkdownPdf
from markdown_pdf import Section
# from ollama import chat
# from ollama import ChatResponse

# --------- choose backend ----------
USE_OLLAMA = False

# --------- OpenAI ---------------
if not USE_OLLAMA:
    from openai import OpenAI

# --------- Ollama ---------------
def call_ollama(model: str, prompt: str) -> str:
    """
    Very lightweight wrapper around `ollama run`
    Make sure you have the model pulled locally (e.g., `ollama pull llama4`).
    """
    import subprocess, json as pyjson, tempfile
    cmd = ["ollama", "run", model, prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

# --------- Prompts ---------------
from prompts import STRUCTURE_PROMPT, RESUME_PROMPT, COVER_LETTER_PROMPT


# --------- OpenAI ---------------
def call_openai(model: str, system: str, user: str) -> str:
    client = OpenAI(api_key=os.getenv("OLLAMA_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system","content": system},
            {"role": "user","content": user,}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content

# --------- Helper Function -----------
def llm_json(prompt: str, model_openai="gpt-4o-mini",model_ollama="llama4") -> str:
    if USE_OLLAMA:
        out = call_ollama(model_ollama, prompt)
    else:
        out = call_openai(model_openai, "You output only valid JSON.", prompt)
    out = out.strip().strip("`")
    if out.startswith("json"):
        out = out[4:].strip()
    print(out)
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        # try a crude fix
        start = out.find("{")
        end = out.rfind("}")
        if start != -1 and end != -1:
            return json.loads(out[start:end + 1])
        print(f"Error while parsing JSON, {e}")
        raise e


# --------- Renderer -----------
def render_md(data: dict, template_name: str, template_path="templates") -> str:
    env = Environment(loader=FileSystemLoader(template_path), autoescape=False)
    template = env.get_template(template_name)
    return template.render(data)

def main():
    load_dotenv()
    jd_path = "job_description.txt"
    with open(jd_path) as f:
        jd = f.read()

    # 1) Extract structure
    print("\n[bold yellow]Extracting requirements...[/bold yellow]")
    structure = llm_json(STRUCTURE_PROMPT.format(jd=jd))

    # 2) Generate fictitious resume
    print("[bold yellow]Generating fictitious resume...[/bold yellow]")
    resume_json = llm_json(RESUME_PROMPT.format(structured_requirements=json.dumps(structure, indent=2)))

    # 3) Render Resume
    print("[bold yellow]Rendering resume markdown...[/bold yellow]")
    md = render_md(resume_json, template_name="resume.md.j2")

    out_path_resume_md = "generated_resume.md"
    out_path_resume_pdf = "resume.pdf"
    with open(out_path_resume_md, "w", encoding="utf-8") as f:
        f.write(md)

    print("[bold yellow]Rendering resume pdf...[/bold yellow]")
    save_file(in_path=out_path_resume_md, out_path=out_path_resume_pdf)

    # 4) Generate fictitious cover letter
    print("[bold yellow]Generating cover letter...[/bold yellow]")
    cover_letter_json = llm_json(COVER_LETTER_PROMPT.format(structured_requirements=json.dumps(structure, indent=2), resume_data=json.dumps(resume_json, indent=2)))

    #5) Render Cover Letter
    print("[bold yellow]Rendering cover letter markdown...[/bold yellow]")
    md = render_md(cover_letter_json, template_name="cover_letter.md.j2")

    out_path_cover_letter_md = "generated_cover_letter.md"
    out_path_cover_letter_pdf = "cover_letter.pdf"
    with open(out_path_cover_letter_md, "w", encoding="utf-8") as f:
        f.write(md)

    print("[bold yellow]Rendering cover letter pdf...[/bold yellow]")
    save_file(in_path=out_path_cover_letter_md, out_path=out_path_cover_letter_pdf)

    print(f"\n[bold green]Done![/bold green] → {out_path_resume_pdf, out_path_cover_letter_pdf}")
    print("\n[dim]Heads-up: Using fictitious credentials to actually apply can be unethical or violate terms. Use responsibly.[/dim]")

def save_file(in_path: str, out_path: str):
    try:
        pdf = MarkdownPdf(toc_level=2, optimize=True)
        text = ""
        with open(in_path) as f:
            text = f.read()
        pdf.add_section(Section(text, paper_size="A4"))
        pdf.meta["title"] = out_path.strip(".pdf")
        pdf.meta["author"] = "Sumeet Singh Aulakh"
        pdf.save(out_path)
    except Exception as e:
        print(f"Error while generating {out_path} pdf. {e}")

if __name__ == "__main__":
    main()