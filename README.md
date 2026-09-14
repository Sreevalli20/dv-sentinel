# DV Sentinel
#t.me/dv_sentinel_engineer_bot

**Domain-specific Design Verification Engineer accessible through communication channels you already use.**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Problem

Design Verification (DV) engineers, VLSI students, RTL designers, and FPGA developers often need quick answers to verification questions:

- How do I prevent FIFO overflow?
- Why is my AXI transaction hanging?
- What coverage points should I add?
- Can you generate an SVA assertion for this protocol?
- Turn this simulation failure into a bug report.

Current solutions require switching between tools, documentation, and forums—breaking workflow and slowing down verification progress.

## Solution

**DV Sentinel** is a domain-specific DV engineer that lives inside communication channels you already use (Telegram, Email). It provides deterministic, rule-based analysis for SystemVerilog, FIFO, AXI, APB, assertions, coverage, and test planning—without requiring external LLMs or simulators.

## Target Users

- VLSI students learning verification
- Junior DV engineers
- RTL designers needing verification support
- FPGA developers debugging protocols
- Verification engineers planning coverage and test plans

## Why DV Engineers Need This

- **Immediate access** to DV expertise without leaving your workflow
- **Deterministic analysis** based on verification best practices
- **Actionable artifacts**: SVA assertions, test plans, coverage suggestions, bug reports
- **Protocol-specific guidance** for FIFO, AXI, APB
- **Learning reinforcement** through daily challenges and interview questions

## Why Caspian

Caspian enables **one shared handler** for multiple communication channels. DV Sentinel uses a single DV intelligence engine that responds identically on Telegram and Email—no duplicated business logic, consistent experience across channels.

## Multi-Channel Architecture

```
Telegram ──┐
           │
Email  ────┼──► Caspian ──► Shared DV Handler ──► DV Intelligence Engine ──► Response
           │
           └─────────────────────────────────────────────────────────────────────┘
```

The same handler processes messages from both channels, ensuring consistent DV expertise regardless of how you reach it.

## Features

### Protocol Analysis
- **FIFO**: Detect read-while-empty, write-while-full, pointer synchronization issues
- **AXI**: Handshake violations, payload stability, deadlock analysis
- **APB**: Timing violations, protocol state analysis

### Assertion Generation
- SVA templates for common scenarios
- VALID/READY handshake assertions
- Reset assertions
- FSM transition assertions

### Coverage Planning
- FIFO coverage points (empty, full, overflow, underflow, reset)
- AXI coverage (channels, bursts, responses, backpressure)
- APB coverage (transfers, wait states, error responses)
- Reset coverage scenarios

### Test Planning
- Professional test plan structure
- Objectives, stimulus, expected behavior
- Corner cases, assertions, coverage
- Negative tests and exit criteria

### Bug Reporting
- Structured bug reports from problem descriptions
- Severity assessment
- Likely root cause analysis
- Suggested regression tests and assertions

### Learning Tools
- **Daily Challenge**: One DV verification challenge per day
- **Interview Mode**: DV interview questions with model answers
- Topics: SystemVerilog, UVM, SVA, protocols, coverage, constrained random

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and overview |
| `/help` | Show all available commands |
| `/status` | System status and configuration |
| `/verify <code>` | Analyze SystemVerilog code |
| `/assert <request>` | Generate SVA assertion |
| `/debug <issue>` | Debug a verification problem |
| `/testplan <component>` | Generate test plan |
| `/coverage <topic>` | Get coverage suggestions |
| `/axi <question>` | AXI protocol help |
| `/apb <question>` | APB protocol help |
| `/fifo <question>` | FIFO verification help |
| `/bug <description>` | Generate bug report |
| `/interview [topic]` | DV interview question |
| `/daily` | Daily verification challenge |
| `/reset <question>` | Reset verification help |

## Telegram Usage

1. Start a chat with **@dv_sentinel_engineer_bot**
2. Send `/start` to begin
3. Use commands or ask questions in plain English

**Example conversation:**
```
You: /assert FIFO should never read when empty
DV Sentinel: [SVA assertion with explanation]

You: Why is my AXI write transaction stuck?
DV Sentinel: [Deadlock analysis and common causes]

You: /coverage FIFO
DV Sentinel: [FIFO coverage suggestions]
```

## Email Usage

1. Email is configured through Caspian
2. Send emails to your configured DV Sentinel address
3. Receive responses with DV analysis

**Setup:** See [Caspian Setup](#caspian-setup) below.

## Example Conversations

### FIFO Debugging
```
You: /verify logic rd_ptr, wr_ptr; always @(posedge clk) if (rd_en) data_out <= mem[rd_ptr];
DV Sentinel: DV SENTINEL ANALYSIS
═══════════════════════════════
1. Potential read while empty [HIGH]
   Read enable may be asserted when FIFO is empty
   Fix: Add empty check: if (!empty) rd_en <= ...
   
   Suggested Assertion:
   assert property (@(posedge clk) empty |-> !rd_en)
```

### AXI Debugging
```
You: /axi Why is my write transaction stuck?
DV Sentinel: Common AXI Deadlock Causes:
1. VALID dropped before READY
2. READY never asserted
3. Response not consumed
4. Reset blocking channel
5. Outstanding transaction limit
```

### Coverage Planning
```
You: /coverage AXI
DV Sentinel: SUGGESTED COVERAGE: AXI
═══════════════════════════════
• Write address channel handshake
• Write data channel handshake
• Burst lengths: 1, 4, 8, 16
• Response types: OKAY, EXOKAY, SLVERR, DECERR
• Outstanding transactions
• Backpressure on each channel
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Communication Channels                    │
│  ┌──────────┐  ┌──────────┐                                 │
│  │ Telegram │  │  Email   │                                 │
│  └────┬─────┘  └────┬─────┘                                 │
└───────┼─────────────┼──────────────────────────────────────┘
        │             │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │   Caspian   │
        │   Gateway   │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │ DV Handler  │
        │  (Shared)   │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │ DV Analyzer │
        │  (Engine)   │
        └──────┬──────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼───┐  ┌──▼───┐
│ FIFO  │  │ AXI  │  │ APB  │
└───────┘  └──────┘  └──────┘
```

## Technology Stack

- **Language**: Python 3.12
- **Web Framework**: FastAPI
- **Communication**: Caspian SDK
- **Database**: SQLite
- **Testing**: pytest
- **Deployment**: Docker, Render

**NOT used**: No external LLMs, no vector databases, no Redis (unless required by Caspian SDK).

## Local Setup

### Prerequisites
- Python 3.12 (or use Docker)
- pip or uv

### Installation

```bash
# Clone repository
git clone https://github.com/Sreevalli20/dv-sentinel.git
cd dv-sentinel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Run Demo Mode (No API Keys)

```bash
# Set demo mode
export DEMO_MODE=true

# Run interactive demo
python -m demo.demo

# Or run scripted demo
python -m demo.demo --scripted
```

### Run Production

```bash
# Set your credentials in .env
export CASPIAN_API_KEY=your_key
export TELEGRAM_BOT_TOKEN=your_token

# Start the application
python -m app.main
```

The application will:
1. Start FastAPI on port 8000
2. Connect to Caspian
3. Add configured channels (Telegram, Email)
4. Process incoming messages

## Docker Setup

### Build Image

```bash
docker build -t dv-sentinel:latest .
```

### Run Container

```bash
# Demo mode
docker run -p 8000:8000 -e DEMO_MODE=true dv-sentinel:latest

# Production with credentials
docker run -p 8000:8000 \
  -e CASPIAN_API_KEY=your_key \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e EMAIL_USERNAME=dv-sentinel \
  dv-sentinel:latest
```

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

## Caspian Setup

### 1. Get Caspian API Key

```bash
# Install Caspian CLI
pip install caspian-sdk

# Sign in (writes to .env)
caspian init project
```

Or get your key from: https://dashboard.trycaspianai.com

### 2. Configure Environment

Add to `.env`:
```
CASPIAN_API_KEY=your_api_key
CASPIAN_BASE_URL=https://api.trycaspianai.com
```

### 3. Connect Telegram

Get bot token from BotFather: https://t.me/BotFather

Add to `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token
```

The application will automatically add the Telegram channel on startup.

### 4. Connect Email

Choose your email username (part before @agents.trycaspianai.com)

Add to `.env`:
```
EMAIL_USERNAME=dv-sentinel
```

The application will automatically add the email channel on startup and display your email address.

## Render Deployment

### Prerequisites
- Render account
- Caspian API key
- Telegram bot token (optional)

### Steps

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Render Service**
- Go to Render dashboard
- Click "New +"
- Select "Web Service"
- Connect your GitHub repository
- Select `dv-sentinel`
- Choose Docker environment
- Region: Oregon (or closest)

3. **Configure Environment Variables** (in Render dashboard)
```
CASPIAN_API_KEY=your_actual_key
CASPIAN_BASE_URL=https://api.trycaspianai.com
TELEGRAM_BOT_TOKEN=your_actual_token
EMAIL_USERNAME=dv-sentinel
PORT=8000
```

4. **Deploy**
- Click "Create Web Service"
- Render will build and deploy
- Your service will be available at `https://your-service.onrender.com`

5. **Verify**
```bash
curl https://your-service.onrender.com/health
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CASPIAN_API_KEY` | Yes (production) | Caspian API key |
| `CASPIAN_BASE_URL` | No | Caspian gateway URL (default: https://api.trycaspianai.com) |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token from BotFather |
| `EMAIL_USERNAME` | No | Email username for @agents.trycaspianai.com |
| `PORT` | No | Application port (default: 8000) |
| `DATABASE_PATH` | No | SQLite database path (default: dv_sentinel.db) |
| `DEMO_MODE` | No | Run without API keys (default: false) |

## Security

- **Secrets never committed**: All credentials in environment variables
- **No secrets in code**: `.env.example` contains placeholders only
- **No secrets in logs**: Sensitive data never logged
- **Input sanitization**: Message size limits, no code execution
- **No shell execution**: User commands never executed
- **No HDL execution**: SystemVerilog analyzed statically, not executed

## Limitations

**Important: DV Sentinel is a hackathon prototype with specific limitations:**

1. **Deterministic analysis ≠ Formal verification**: Pattern-based analysis is not equivalent to formal verification tools
2. **No HDL execution**: SystemVerilog is analyzed statically; no simulation or compilation
3. **Validate assertions**: Generated assertions must be validated against your specific design requirements
4. **Protocol assumptions**: Guidance assumes standard protocol variants; your design may differ
5. **No external LLM**: Intelligence is rule-based, not AI-generated
6. **Static analysis only**: Cannot detect dynamic issues requiring simulation

**Always verify** generated assertions, test plans, and analysis against your actual design specifications.

## Future Roadmap

- [ ] UVM testbench template generation
- [ ] Scoreboard and monitor suggestions
- [ ] Reference model guidance
- [ ] Constraint randomization help
- [ ] More protocol support (AHB, PCIe, USB)
- [ ] Waveform analysis guidance
- [ ] Integration with popular simulators
- [ ] Web UI for interactive analysis
- [ ] Team collaboration features

## Testing

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test

```bash
pytest tests/test_fifo.py
```

### Run with Coverage

```bash
pytest --cov=app --cov=agent --cov=dv --cov=storage tests/
```

### Test Coverage

Tests cover:
- Command routing
- Natural language intent detection
- FIFO, AXI, APB rules
- SVA generation
- Coverage generation
- Test plan generation
- Bug report generation
- Interview mode
- Daily mode
- Response formatting
- SQLite operations
- FastAPI endpoints
- Configuration validation
- Error handling

**Note**: External Caspian calls are mocked in tests—no real API keys required.

## Demo Instructions

### Interactive Demo

```bash
export DEMO_MODE=true
python -m demo.demo
```

Try commands:
```
/start
/assert FIFO should never read when empty
/axi Why is my write transaction stuck?
/coverage FIFO
/testplan FIFO
/bug My simulation failed
/interview
/daily
```

### Scripted Demo

```bash
python -m demo.demo --scripted
```

This runs through predefined scenarios automatically.

## Hackathon Judging Strategy

### Message Volume & Usage (40%)

**Recurring commands for engagement:**
- `/daily` - Daily verification challenge encourages repeat usage
- `/interview` - Learning tool for students and engineers
- `/coverage` - Practical workflow for verification planning
- `/assert` - Common need in verification
- `/debug` - Debugging assistance

**Multi-channel reach:**
- Telegram for quick questions
- Email for detailed analysis and documentation

### Use Case & Impact (25%)

**Target users:**
- VLSI students learning verification
- Junior DV engineers needing guidance
- RTL designers without DV expertise
- FPGA developers debugging protocols

**Impact:**
- Reduces time to find verification answers
- Provides structured artifacts (assertions, test plans, bug reports)
- Learning reinforcement through daily challenges and interview questions

### Creativity (20%)

**Positioning:**
"An always-available DV engineer inside communication channels"

**Differentiation:**
- Domain-specific (not generic chatbot)
- Deterministic rule-based engine (no external LLM required)
- Multi-channel through Caspian (single handler, consistent experience)
- Actionable verification artifacts (not just text explanations)

### Implementation (15%)

**Demonstrated:**
- Real Caspian integration
- Two channels (Telegram + Email)
- Shared handler architecture
- Structured DV engine (FIFO, AXI, APB, SVA, coverage, test plans, bug reports)
- Persistent context (SQLite)
- Comprehensive tests (pytest)
- Docker deployment (Python 3.12)
- Render deployment configuration
- Secure secrets management (environment variables)
- Clean GitHub repository
- Demo mode without API keys

## Why This Is Not Just Another Chatbot

1. **Domain Specialization**: Built specifically for Design Verification, not general-purpose
2. **Repeatable DV Workflows**: Structured outputs for assertions, test plans, coverage, bug reports
3. **Actionable Artifacts**: Generates SVA code, test plans, coverage points—not just explanations
4. **Multi-Channel Communication**: Same expertise on Telegram and Email through Caspian
5. **Deterministic Intelligence**: Rule-based engine, no external LLM required
6. **Safe Analysis**: Static pattern analysis, no HDL execution
7. **Useful Recurring Features**: `/daily` challenges, `/interview` questions for engagement
8. **Protocol-Specific**: Deep knowledge of FIFO, AXI, APB protocols

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## Acknowledgments

- Built for Caspian AI Agent Challenge
- Uses Caspian SDK for multi-channel communication
- Design Verification community for domain knowledge

---

**DV Sentinel** - Your Design Verification Engineer, wherever you are.
