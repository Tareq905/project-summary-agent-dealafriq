# AI Agent Server for Project Management System

## Overview

This AI Agent Server is designed to work alongside a Project Management System backend.  
It continuously fetches structured project data from PMS backend APIs, processes them through multiple AI agents, and generates session based project intelligence outputs.

This server does not store any primary project data locally.  
All analysis is performed only on the structured JSON received from PMS backend APIs.

The system supports three operational project sessions:

- ONGOING
- COMPLETED
- CANCELLED


---

## Architecture Flow

PMS Backend → AI Agent Server → AI Agents → Structured JSON Output → PMS Backend Dashboard


The AI Agent Server continuously performs:

- Project Data Fetching
- Activity Log Fetching
- Context Mapping
- Session Segregation
- AI Analysis
- Summary Generation


---

## AI Intelligence Layer

This system combines:

### Neuro Symbolic Logic (NSL)

Requirement driven logical reasoning is applied on:

- Project Tasks
- Milestones
- Meetings
- Health Score
- Activity Logs
- Dependencies
- Decisions

NSL ensures deterministic interpretation of structured backend inputs instead of probabilistic prediction.

Example reasoning includes:

- Pending tasks with near deadlines
- Upcoming milestones
- Repeated unresolved action points
- Declining health scores
- Task completion trends
- Communication frequency
- Risk indicators


### Retrieval Augmented Generation (RAG)

Relevant contextual information is dynamically retrieved from:

- Meeting Key Points
- Action Points
- Documents
- Project Logs
- Project Metadata

Retrieved structured inputs are then passed into LLM for semantic summarization.

LLM performs contextual summarization only.  
No statistical prediction or confidence score is generated unless validated numeric backend data is provided.


---

## Agents Included

Each agent processes PMS backend data independently for each session.


### Weekly Summary Agent
Generates weekly progress summary based on:

- Meeting Key Points
- Action Points
- Task Updates
- Activity Logs


### Project Summary Agent
Generates high level project overview using:

- Task Status
- Milestones
- Health Score
- Recent Meeting Outcomes


### Meeting Summary Agent
Summarizes:

- Meeting Notes
- AI Identified Risks
- Key Discussion Topics
- Assigned Action Points


### Document Summary Agent
Analyzes:

- Uploaded Project Documents
- Agreements
- Supporting Files

Generates AI Document Summary.


### Health Score Agent
Computes project score based on:

- Task Completion Rate
- Meeting Resolution Status
- Milestone Progress
- Health Score from Backend


---

## Session Based Processing

For each session:

### ONGOING
- Active Tasks Analysis
- Upcoming Milestones
- Pending Action Points
- Latest Meeting Summary
- Current Health Score

### COMPLETED
- Final Deliverables Review
- Completed Milestone Analysis
- Final Meeting Summary
- Closure Health Evaluation

### CANCELLED
- Incomplete Task Identification
- Cancelled Milestone Review
- Cancellation Discussion Summary
- Last Known Health Score


---

## Output Format

Each project will produce structured output:

```json
{
  "projectId": "PRJ-001",
  "projectSummary": "...",
  "weeklyMeetingSummary": "...",
  "projectScore": 8.7,
  "documents": [],
  "meetings": [],
  "latestMeetingSummary": "..."
}

```
---

# AI Agent Server

This is the FastAPI based AI Agent backend for Project Analysis inside the multi agent Project Management System.

---

## Installation Guide

### Step 1: Clone Repository

```bash
git clone <repository_url>
cd ai-agent-server
```

---

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

---

### Step 3: Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Create a `.env` file in the project root directory and add the following:

```env
OPENAI_API_KEY=your_openai_api_key

ONGOING_PROJECT_API=your_ongoing_project_api
COMPLETED_PROJECT_API=your_completed_project_api
CANCELLED_PROJECT_API=your_cancelled_project_api

ONGOING_LOG_API=your_ongoing_log_api
COMPLETED_LOG_API=your_completed_log_api
CANCELLED_LOG_API=your_cancelled_log_api
```

---

## Run Server

```bash
python -m uvicorn main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```
