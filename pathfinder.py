import os
import json
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from rich import print
from markdown_pdf import MarkdownPdf
from markdown_pdf import Section
import datetime
from ollama import chat
from ollama import ChatResponse

# --------- choose backend ----------
USE_OLLAMA = True

# --------- OpenAI ---------------
if not USE_OLLAMA:
    from openai import OpenAI

# ---------Tools Definitions------
def get_current_date() -> str:
    """
    Get the current date as a string
    :return: Date in format Month DD, YYYY
    """
    x = datetime.datetime.now()
    return x.strftime("%B %d, %Y")

get_current_date_tool = {
    "type": "function",
    "function": {
        "name": "get_current_date",
        "description": "Get the current date as a string",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {}
        }
    }
}


# --------- Ollama ---------------
def call_ollama(model: str, prompt: str) -> str:
    """
    Very lightweight wrapper around `ollama run`
    Make sure you have the model pulled locally (e.g., `ollama pull llama4`).
    """
    # import subprocess
    # cmd = ["ollama", "run", model, prompt]
    # result = subprocess.run(cmd, capture_output=True, text=True)
    # return result.stdout.strip()
    messages = [
        {
            "role": "system",
            "content": f"You output only valid JSON. Remember to get date from get_current_date tool"
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]

    available_functions = {
        "get_current_date": get_current_date,
    }

    while(True):
        response = chat(model, messages=messages, tools=[get_current_date_tool])
        print(response)

        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                if function_to_call :=available_functions.get(tool.function.name):
                    print(f"Calling {tool.function.name}...")
                    output = function_to_call(**tool.function.arguments)
                    print("Function output:", output)
                else:
                    print(f"No function found: {tool.function.name}.")

        if response.message.tool_calls:
            messages.append(response.message)
            messages.append({
                "role": "tool",
                "content": str(output),
                "tool_name": tool.function.name,
            })
        else:
            return response.message.content




# --------- Prompts ---------------
from prompts import STRUCTURE_PROMPT, RESUME_PROMPT, COVER_LETTER_PROMPT

# --------- Tools for openAI ------
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_date",
        "description": "Get the current date",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
}]

# --------- OpenAI ---------------
def call_openai(model: str, system: str, user: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
                {"role": "system","content": system},
                {"role": "user","content": user,}
            ]
    while (True):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.4
        )
        print(response)

        msg = response.choices[0].message
        if hasattr(msg, "tool_calls") and msg.tool_calls :
            tool_call = msg.tool_calls[0]
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        }
                    }
                ]
            })
            if tool_call.function.name == "get_current_date":
                date = get_current_date()
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id ,
                    "content": date
                })
                continue
        else:
            return msg.content

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
    # print(call_ollama("llama4", "What is the date today?"))