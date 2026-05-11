# MediAssist-MCP Demo Script

## 1. Quick 2-3 Minute Live Demo

1. Open the Streamlit frontend.
2. Start with **Symptom checker** and enter `fever`.
3. Move to **Emergency triage** and enter `chest pain and shortness of breath`.
4. Show **Medicine info** with `ibuprofen`.
5. Show **BMI calculator** with the default inputs.
6. Show **Nutrition recommendation** for `diabetes`.
7. Show **Appointment scheduler** with a sample name and date.
8. Finish with **Mental health support** and `stressed`.
9. Mention that the MCP server exposes the same logic to AI clients through FastMCP.

## 2. Demo Video Talking Points

- The project is synthetic-only and does not use real patient data.
- The architecture is intentionally simple so it is reliable under hackathon time pressure.
- The same local logic powers both the MCP server and the Streamlit frontend.
- The tool set covers practical healthcare workflows:
  symptom checking, triage, BMI, medicines, nutrition, scheduling, risk, and wellness support.
- The project is ready to connect to a Prompt Opinion Marketplace style catalog through MCP.
- No paid APIs or API keys are required.
- Optional Ollama support can be added later, but the core build already works fully offline.

## 3. Terminal Commands

```bash
cd "/Users/siva/Documents/Copy 2/New/MediAssist-MCP"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python server.py
```

In a second terminal for the Streamlit frontend:

```bash
cd "/Users/siva/Documents/Copy 2/New/MediAssist-MCP"
source .venv/bin/activate
streamlit run frontend/app.py
```

For MCP Inspector testing with HTTP transport:

```bash
cd "/Users/siva/Documents/Copy 2/New/MediAssist-MCP"
source .venv/bin/activate
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 MCP_PORT=8000 python server.py
```

Then connect the Inspector to:

```text
http://127.0.0.1:8000/mcp
```

## 4. Judge-Ready Pitch

MediAssist-MCP is a lightweight healthcare MCP server that proves real interoperability without the weight of a full clinical system.
It is easy to demo, easy to understand, and safe because every example is synthetic.
