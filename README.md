# Socratikal: A Learning Project in Agentic Design

**An experimental agentic system built to explore advanced orchestration patterns and the fundamentals of AI-driven dialogue.**

This project serves as a hands-on exercise in agentic architecture. The goal was not to build a production-ready application, but to move beyond simple Q&A bots and implement a more complex, multi-step reasoning workflow from first principles.

The core challenge I set for myself was to build an agent that could emulate a Socratic dialogue. Given a topic, can an AI system generate, critique, and select a truly thought-provoking question to guide a conversation?

This project is the result of that exploration, focusing on two key learning objectives:

1.  **Mastering Advanced Agentic Patterns:** Moving beyond a simple "tool-using" agent to implement concepts like:
    *   **Dynamic Planning:** An agent that generates its own plan of action (a list of subjects) before executing.
    *   **Self-Correction & Refinement:** An agent that generates multiple candidate outputs and then uses a separate cognitive step to critique and select the best one.
    *   **Stateful, Cyclical Workflows:** Building an agent that can maintain a continuous, looping conversation.

2.  **Framework Exploration:**
    *   This project was built using **[PocketFlow](https://github.com/huggingface/pocketflow/blob/main/pocketflow.py)**, a lean, ~100-line state machine framework.
    *   The choice was deliberate: by using a minimal, "glass box" framework, I was forced to implement the core state management and transition logic myself, leading to a deeper, first-principles understanding of how these agentic systems are orchestrated.

## The "Socratikal" Architecture

The system is a proof-of-concept of a cyclical, three-stage graph designed to find the "best" question to ask next.

1.  **The Planner (`Socratikal` Node):** Takes the conversation history and generates a list of potential subjects to explore.
2.  **The Expander (`GeneratingQuestions` Node):** Takes the list of subjects and generates a high-quality, conversational question for each one in parallel.
3.  **The Critic (`Ranker` Node):** Takes all the generated questions and uses a final LLM call to select the single most insightful and conversation-forwarding question to present to the user.

The user's response to this question is then fed back into the history, and the cycle repeats.

## How to Run

This project is built with Python and requires a `.env` file with your Gemini API key.

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd socratikal
    ```

2.  **Set up the environment (using UV):**
    ```bash
    # It is recommended to use a virtual environment
    uv venv
    uv pip install -r requirements.txt
    ```

3.  **Create your environment file:**
    Create a `.env` file in the root of the project and add your API key:
    ```
    API_KEY="your_google_gemini_api_key"
    ```

4.  **Run the agent:**
    ```bash
    uv run python main.py
    ```

## Key Learnings & Future Work

This experiment was a success from a learning perspective. It provided deep insights into the challenges of managing agent state, orchestrating multi-step LLM calls, and the power of self-critique loops.

Future work could involve:
*   **Error Handling:** Implementing more robust error handling for failed LLM calls.
*   **State Persistence:** Adding a mechanism to save and load dialogues.
*   **Framework Comparison:** Re-implementing the same logic in a more abstracted framework like LangGraph to compare the developer experience and debugging challenges.

Still this exploration is "complete"
