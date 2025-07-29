# Pathfinder

Pathfinder is the application that will help you land your dream job. It generates the resumes and cover letters for you according to your personal information, projects. It understands the job description and your abilities, and then generates resume and cover letter curated according to the job description.

## Features

- Generates resume and cover letters using the power of LLMs.
- Generates resume and cover letters using the power of local LLMs using ollama.
- Converts the generated resume and cover letters into PDFs.

## Getting Started

To get started with using pathfinder we need to setup the project locally. To get a local copy of the project clone the repository and follow the steps as follows.

## Prerequisites

- Git, Python3, OpenAI API key, and Ollama for local models.

1. Clone the repository
```bash
git clone https://github.com/Sumeet-Aulakh/pathfinder
```

2. Install the dependecies

```bash
pip3 install -r requirements.txt
```

3. Set up the environment variables : .env in root directory

```.env
OPENAI_API_KEY="sk-proj-..."
```
**Note:** You can get the openai api key from [here](https://platform.openai.com/account/api-keys).

4. Set up custom prompts: prompts.py in root directory
```python
STRUCTURE_PROMPT="..."
RESUME_PROMPT="..."
COVER_LETTER_PROMPT="..."
```
**Note:** Check prompts.py.example for example prompts, just add custom rules there. 
To get perfect prompts that work contact me😇.

## Usage
1. Copy and paste the job description into job_description.txt in root directory of project.
2. To use the pathfinder we need to run the following command.

```bash
python3 pathfinder.py
```

# For Local Models

Local models are supported by ollama. To use the local models we need to have the ollama installed in our system. You can install ollama by following the instructions [here](https://github.com/ollama/ollama).

For the project following model is recommended:
- [llama4](https://ollama.com/library/llama4)

### Examples
Generated examples can be found in [example](https://github.com/Sumeet-Aulakh/pathfinder/tree/master/examples) directory

## Contributing

Contributions are welcome! Please feel free to submit a pull request.
