## 🛠️ Developer Documentation
This section provides an overview of the internal architecture, modules, and workflow of the Voice Scheduling Agent.

---
### 🧱 Project Architecture
The project follows a **modular structure** separating responsibilities:
```
backend/
│── tools.py      # Business logic (meeting scheduling)
│── llm.py        # LLM interaction + tool calling
│── audio.py      # Speech-to-text & text-to-speech
│── utils.py      # Shared constants
app.py            # Streamlit frontend
```
---
### 🔄 Application Flow
1. User provides input (text or voice)
2. Audio (if present) → converted using `speech_to_text`
3. Input is appended to conversation history
4. Conversation is sent to the LLM (`chat()` function)
5. LLM may:
   * Respond normally
   * Trigger a tool (`schedule_meeting`)
6. If tool is triggered:
   * Backend executes function
   * Result is added to conversation
   * LLM generates final response
7. Response is:
   * Displayed in UI
   * Converted to speech (`text_to_speech`)
8. Meeting (if created) is stored and shown in sidebar
---
### 📦 Module Breakdown
#### 1. `tools.py`
Handles core business logic.
* `schedule_meeting(...)`
  * Parses date, time, and duration
  * Computes start/end timestamps
  * Generates Google Calendar event link
  * Returns structured meeting dictionary
---
#### 2. `llm.py`
Manages interaction with the a Cohere's LLM.
* Defines:
  * `system_prompt` (strict behavior rules)
  * `tools` (function schema for tool calling)
* `chat(conversation)`
  * Sends conversation to LLM
  * Detects tool calls
  * Executes backend functions
  * Returns final response + optional meeting
---
#### 3. `audio.py`
Handles voice processing.
* `speech_to_text(audio)`
  * Uses Google Speech Recognition
  * Returns text or `[Unclear Audio]`
* `text_to_speech(text)`
  * Uses gTTS
  * Returns path to generated `.mp3`
---
#### 4. `utils.py`
Defines shared constants.
* `MeetingDetails` enum
* Key aliases:
  * `host_name_key`
  * `date_key`
  * `time_key`
  * `duration_key`
  * `title_key`
  * `link_key`
---
#### 5. `app.py`
Streamlit frontend.
Responsibilities:
* UI rendering (chat + sidebar)
* Session state management
* Handling user input (text/audio)
* Calling backend (`chat`)
* Playing audio responses
* Displaying scheduled meetings
---
### 🧠 LLM Behavior Design
The assistant is intentionally **strict and deterministic**:
* Must collect:
  * Host name
  * Date (with year)
  * Time
  * Duration
  * Title (optional)
* Must validate inputs before proceeding
* Must confirm with user before scheduling
* Cannot assume missing data
* Cannot perform tasks outside scheduling
This ensures:
* Predictable tool usage
* Clean structured outputs
* Better reliability in production
---
### 🔌 Tool Calling Mechanism
The LLM uses structured tool calling:
1. LLM decides to call `schedule_meeting`
2. Arguments are passed from a JSON string
3. Backend executes:
   ```python
   schedule_meeting(**json.loads(arguments))
   ```
4. Result is appended as:
   ```python
   {
       "role": "tool",
       "content": ...
   }
   ```
5. LLM generates final user-facing response
---
### 🧾 Data Format
Each meeting is stored as:
```python
{
    "host_name": str,
    "date": str,
    "time": str,
    "duration": str,
    "title": Optional[str],
    "link": str
}
```
---
### ⚠️ Edge Case Handling
* Unclear audio → `[Unclear Audio]`
* Missing fields → LLM asks only for missing data
* Missing year → explicitly requested
* Multiple values → clarification required
* Post-confirmation changes → re-confirmation required
---
### 🚀 Extending the Project
You can easily extend the system by:
* Adding new tools (e.g., cancel meeting, reschedule)
* Replacing Cohere with another LLM provider
---
### 📌 Summary
This project demonstrates:
* LLM + tool integration
* Voice-enabled interfaces
* Structured conversational workflows
* Clean separation of frontend and backend logic