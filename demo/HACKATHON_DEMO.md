# DV Sentinel Hackathon Demo Script

**Duration:** 3-5 minutes

---

## Demo Overview

This demo showcases DV Sentinel, a domain-specific Design Verification engineer accessible through Telegram and Email channels via Caspian SDK.

---

## Demo Sequence

### 1. Introduction (30 seconds)

**Narrator:** "DV Sentinel is your always-available Design Verification engineer. It lives inside communication channels you already use - Telegram and Email - and provides deterministic, rule-based analysis for SystemVerilog, FIFO, AXI, APB, assertions, coverage, and test planning."

**Show:** 
- GitHub repository: https://github.com/Sreevalli20/dv-sentinel
- Architecture diagram from README

---

### 2. Telegram Demo (2 minutes)

**Action:** Open Telegram and chat with @dv_sentinel_engineer_bot

**Command 1:** `/start`
```
You: /start
DV Sentinel: [Shows welcome message with capabilities]
```

**Command 2:** `/assert FIFO should never read when empty`
```
You: /assert FIFO should never read when empty
DV Sentinel: [Generates SVA assertion with explanation]
```

**Command 3:** `/axi Why is my write transaction stuck?`
```
You: /axi Why is my write transaction stuck?
DV Sentinel: [Shows AXI deadlock analysis with 5 common causes]
```

**Command 4:** `/coverage FIFO`
```
You: /coverage FIFO
DV Sentinel: [Lists 14 FIFO coverage points]
```

**Command 5:** `/testplan FIFO`
```
You: /testplan FIFO
DV Sentinel: [Generates structured test plan with objectives, stimulus, corner cases]
```

**Command 6:** `/bug My simulation failed with timeout`
```
You: /bug My simulation failed with timeout
DV Sentinel: [Generates structured bug report]
```

**Command 7:** `/daily`
```
You: /daily
DV Sentinel: [Shows daily verification challenge]
```

---

### 3. Natural Language Demo (30 seconds)

**Action:** Ask questions without commands

**Question 1:** "Why can an AXI transaction get stuck waiting for READY?"
```
You: Why can an AXI transaction get stuck waiting for READY?
DV Sentinel: [Provides analysis of READY assertion issues]
```

**Question 2:** "Generate APB verification tests"
```
You: Generate APB verification tests
DV Sentinel: [Shows APB protocol states and test guidance]
```

---

### 4. Multi-Channel Explanation (30 seconds)

**Narrator:** "The same DV Sentinel intelligence engine powers both Telegram and Email channels through Caspian SDK. One shared handler, consistent experience across all channels."

**Show:** 
- Architecture diagram highlighting shared handler
- Email configuration in .env.example

---

### 5. GitHub Repository (30 seconds)

**Action:** Show repository structure

**Highlight:**
- Clean architecture: app/, agent/, dv/, channels/, storage/
- Comprehensive tests: 63 passing tests
- Docker support
- Render deployment ready
- Security: .env in .gitignore, secrets in environment variables only

---

### 6. Key Features Recap (30 seconds)

**Narrator:** "DV Sentinel provides:"

- **Protocol Analysis:** FIFO, AXI, APB verification
- **Assertion Generation:** SVA templates for common scenarios
- **Coverage Planning:** Functional coverage suggestions
- **Test Planning:** Professional test plan structure
- **Bug Reporting:** Structured bug reports from descriptions
- **Learning Tools:** Daily challenges and interview questions
- **No LLM Dependency:** Deterministic rule-based engine
- **Multi-Channel:** Telegram + Email via Caspian

---

### 7. Demo Mode (30 seconds)

**Action:** Show local demo mode (no API keys required)

**Command:**
```bash
export DEMO_MODE=true
python -m demo.demo --scripted
```

**Narrator:** "Demo mode works without any API keys, testing the DV intelligence engine locally."

---

## Demo Notes

**What to Emphasize:**
- Real DV use case, not generic chatbot
- Domain-specific knowledge (FIFO, AXI, APB, SVA)
- Actionable artifacts (assertions, test plans, coverage)
- Multi-channel through Caspian (single handler)
- No external LLM required
- Production-ready (Docker, Render, tests)
- Secure (no secrets in code)

**What to Avoid:**
- Don't claim it's formal verification (it's static pattern analysis)
- Don't claim it executes HDL (it's static analysis only)
- Don't claim measured usage numbers
- Don't fabricate live integration results if credentials unavailable

**Backup Plan:**
If live Telegram/Email credentials unavailable, show:
- Demo mode with scripted scenarios
- Test results (63 passing)
- Docker build success
- Repository structure

---

## Demo Conclusion

**Narrator:** "DV Sentinel brings DV expertise to where engineers already work - Telegram and Email. It's a domain-specific, deterministic assistant that generates real verification artifacts without requiring external LLMs. Built for the Caspian AI Agent Challenge."

**Show:** 
- GitHub repository link
- Render deployment configuration
- "Thank you" slide
