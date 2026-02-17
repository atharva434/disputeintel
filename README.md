# Agentic Disputer Risk Intelligence System

A production-grade AI system for analyzing transaction disputes, detecting fraud, and prioritizing risk.

## 🎯 Features
- **Dispute Analysis Agent**: Uses LLMs to classify disputes and detect fraud signals.
- **Risk Scoring**: Auto-assigns Low/Medium/High risk levels.
- **Operational Insights**: Dashboard for tracking trends and top dispute categories.
- **Explainable AI**: Provides step-by-step reasoning for every decision.

## 🚀 Setup & Run

1.  **Clone & Install**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Key**
    Duplicate `.env` and add your OpenAI Key:
    ```bash
    OPENAI_API_KEY=sk-...
    ```

3.  **Initialize Database**
    ```bash
    python manage.py migrate
    python manage.py seed_disputes  # Loads 20 simulated cases
    ```

4.  **Run Server**
    ```bash
    python manage.py runserver
    ```
    Access the dashboard at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 🏗️ Architecture
- **Backend**: Django 5 + SQLite
- **AI Core**: LangChain + OpenAI GPT-4
- **Frontend**: Django Templates + Tailwind CSS

## 📂 Project Structure
- `disputes/`: Main app containing Models, Views, and the `DisputeReasoningAgent`.
- `core/`: Legacy data intelligence module (optional).
- `templates/disputes/`: Tailwind-styled UI templates.
