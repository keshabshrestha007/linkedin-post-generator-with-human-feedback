# 💼 LinkedIn Post Generator

This repository contains a Streamlit application that generates professional LinkedIn posts from a short topic using a LangGraph and Groq's ChatGroq model. The app supports an interactive generate → feedback → refine loop so you can iterate on the output until you're satisfied and download the final post.

---

## 🚀 Features

- Generate a concise, well-structured LinkedIn post from a short topic.
- Iterative human feedback: provide feedback, the model updates the post, repeat until you type `done`.
- Persist conversation threads via an on-disk SQLite checkpointer (`simple_chatbot.sqlite`).
- Adjustable creativity (temperature) via the sidebar slider.
- Download generated content
- Uses Groq API for fast inference

---

## Requirements

- Python 3.13
- Virtual environment recommended
- `GROQ_API_KEY` — required to use Groq's ChatGroq. Put it in a `.env` file or export it in your environment.


---

## 🧠 Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/keshabshrestha007/linkedin-post-generator-with-human-feedback.git

```
```bash
cd linkedin-post-generator-with-human-feedback
```

2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
```
#### on mac
```bash
source venv/bin/activate 
```
#### on windows
```bash
 venv\Scripts\activate 
```

3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

4️⃣ Add your Groq API key.

```bash
copy .env.example .env
# edit .env to set GROQ_API_KEY (no surrounding quotes preferred)
```

5️⃣ Run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

---

## Repo structure


```
.
├── models
|   └── llms.py           
├── prompts
|    └── prompt.py
├── requirements.txt
├── streamlit_app.py            
├── linkedin_post_generator2.py
├── venv         
├── .env
├── .env.example 
├── simple_chatbot.sqlite             
└── README.md
```
---


## How the generate/feedback loop works

- Enter a topic.
- The LangGraph `model` node produces a draft post and the app displays it.
- If the graph triggers an interrupt to collect feedback, the UI will show a feedback input and a "Submit feedback" button. Enter feedback and submit — the graph resumes and updates the post.
- Repeat feedback rounds until you submit `done` (or `d`) — the thread finishes and you may download the final post.

---

## Important implementation notes & troubleshooting

- GROQ API key: if the LLM fails to initialize, verify `GROQ_API_KEY` is set (in `.env` or the environment). The project uses `python-dotenv` to load `.env`.
- Circular imports: `models/llms.py` exposes a `create_llm()` factory. Avoid importing UI state (e.g., temperature slider) directly from Streamlit files into `models/llms.py` — that caused circular imports previously.
- Streamlit duplicate element IDs: dynamic feedback inputs use unique `key` values (based on thread id) and the app avoids `while True` blocking loops so Streamlit can re-run the script cleanly on interactions.
- LangGraph API shapes: `st.py` assumes `app.stream()` yields chunks containing a `model` key with `generated_post`. If your installed LangGraph version returns a different structure, adjust the unpacking in `st.py`.

---

## Development tips

- To change prompts: edit `prompts/prompt.py`.
- To change model or temperature: modify the `create_llm()` call or adjust the Streamlit slider which passes `temperature` into `create_llm()`.
- To reset state: remove `simple_chatbot.sqlite*` files and restart the app.

---

## License

MIT License — adapt as needed.


