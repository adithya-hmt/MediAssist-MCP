# MediAssist-MCP

MediAssist-MCP is a simple, reliable, hackathon-ready healthcare MCP server built with Python and FastMCP.
It exposes synthetic healthcare tools that can plug into MCP clients, the Prompt Opinion Marketplace, and a small Streamlit frontend.

## What MCP Is

MCP stands for Model Context Protocol.
It is a standard way for AI apps to discover tools, call them with structured arguments, and receive structured JSON back.
That makes it a strong fit for hackathon demos where you want interoperability without building a full custom API layer.

## Why This Project Works For The Hackathon

- AI factor: it exposes multiple healthcare tools an AI agent can call
- Potential impact: it covers common demo workflows like triage, medicine lookup, and scheduling
- Feasibility: it is local-only, synthetic-only, and easy to run on a MacBook Apple Silicon

## What Is Included

- Python + FastMCP server
- Streamlit frontend for visual testing
- Local JSON data source
- Modular clean structure
- Structured JSON responses
- Comments and docstrings
- Error handling and logging
- Optional local Ollama helper
- FHIR-ready notes
- SHARP context placeholders
- Marketplace publishing notes

## Folder Layout

```text
MediAssist-MCP/
├── server.py
├── core/
├── data/
├── demo_script.md
├── docs/
├── fhir/
├── frontend/
├── integrations/
├── services/
├── tools/
├── requirements.txt
├── README.md
└── .env.example
```

## Tools Exposed By MCP

1. `symptom_checker(symptom: str)`
2. `emergency_triage(symptoms: str)`
3. `bmi_calculator(weight, height)`
4. `medicine_info(medicine_name: str)`
5. `nutrition_recommendation(condition: str)`
6. `appointment_scheduler(name: str, date: str)`
7. `mental_health_support(mood: str)`
8. `health_risk_assessment(age: int, smoking: bool, diabetes: bool)`

All of them use only synthetic healthcare data and simple local logic.

## Install

```bash
cd "/Users/siva/Documents/Copy 2/New/MediAssist-MCP"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run Locally

### MCP server with stdio transport

```bash
python server.py
```

### MCP server with Streamable HTTP transport

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 MCP_PORT=8000 python server.py
```

### Streamlit frontend

```bash
streamlit run frontend/app.py
```

## Test With MCP Inspector

The easiest inspector flow is Streamable HTTP:

1. Start the MCP server with:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 MCP_PORT=8000 python server.py
```

2. Start the Inspector:

```bash
npx -y @modelcontextprotocol/inspector
```

3. Connect it to:

```text
http://127.0.0.1:8000/mcp
```

If you prefer stdio, launch the server command directly from the Inspector.

## How To Demo For Judges

The best short demo is:

1. Open the Streamlit app.
2. Run `Symptom checker` with `fever`.
3. Show `Emergency triage` with `chest pain and shortness of breath`.
4. Show `Medicine info` with `ibuprofen`.
5. Show `BMI calculator` using the default numbers.
6. Show `Nutrition recommendation` for `diabetes`.
7. Show `Appointment scheduler` with a sample name and date.
8. Finish with `Mental health support`.

That sequence shows breadth, local reliability, and practical healthcare usefulness.

## Prompt Opinion Integration Notes

MediAssist-MCP is designed to be easy to catalog in a Prompt Opinion Marketplace style flow because:

- the tool names are stable and readable
- every response is structured JSON
- no paid API keys are required
- no real patient data is used
- the server can run over stdio or Streamable HTTP

Suggested integration approach:

1. Register the MCP server endpoint in Prompt Opinion.
2. Map each tool name to its schema and sample output.
3. Use the Streamable HTTP endpoint at `http://127.0.0.1:8000/mcp` for live demos.
4. Keep the JSON response shapes stable so agents and marketplace cards stay predictable.

## Marketplace Publishing Steps

1. Confirm the server runs locally with `python server.py`.
2. Confirm the frontend works with `streamlit run frontend/app.py`.
3. Confirm the tools are visible in MCP Inspector.
4. Write a short catalog description that explains the synthetic-only healthcare use case.
5. Publish the MCP endpoint to your marketplace or registry.
6. Add sample tool calls and response examples for judges and reviewers.

## Optional Ollama Support

The project includes `integrations/ollama_optional.py` as a free/local helper.
It is not required for the core demo and is safe to ignore.
If you want to experiment with it, set `OLLAMA_ENABLED=true` in `.env`.

## Safety Note

This project is synthetic by design.
It is useful for prototyping and hackathon demos, but it is not medical advice and it is not a clinical system.

## Terminal Commands

### Full local setup

```bash
cd "/Users/siva/Documents/Copy 2/New/MediAssist-MCP"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Start the MCP server

```bash
python server.py
```

### Start the Streamlit frontend

```bash
streamlit run frontend/app.py
```

### Start the MCP Inspector workflow

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 MCP_PORT=8000 python server.py
npx -y @modelcontextprotocol/inspector
```

## Demo Assets

See `demo_script.md` for a short live demo script, judge-ready talking points, and copy-paste commands.
