# Resume Tailor + Job Tracker

Automatically tailors your resume to job descriptions using Claude AI, and tracks your applications through the hiring pipeline.

## Setup

**1. Install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install anthropic pdfplumber python-docx beautifulsoup4 requests
```

**2. Set your Anthropic API key**
```bash
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.zshrc
source ~/.zshrc
```
Get a key at [console.anthropic.com](https://console.anthropic.com) → API Keys.

---

## Tailor a Resume

```bash
# From a job posting URL (recommended)
./run.sh tailor --url "https://boards.greenhouse.io/company/jobs/123"

# With company/role override (used in output filename)
./run.sh tailor --url "https://..." --company "Stripe" --role "PMM"

# From a saved text file
./run.sh tailor --jd job_description.txt --company "Stripe" --role "PMM"

# Paste manually (type END when done)
./run.sh tailor --company "Stripe" --role "PMM"
```

Tailored resumes are saved to the `output/` folder as both `.txt` and `.docx`. Each run also automatically logs the application to the tracker.

**What Claude does:**
- Reorders bullet points to surface the most relevant experience first
- Mirrors keywords from the job description (for ATS systems)
- Rewrites the summary to speak directly to the role
- Adds a "Tailoring Notes" section explaining every change made

---

## Track Applications

```bash
./run.sh tracker list                        # all applications
./run.sh tracker list --status "Interview"   # filter by stage
./run.sh tracker show 3                      # full details for one application
./run.sh tracker update 3 --status "Phone Screen" --notes "Call Thu 2pm"
./run.sh tracker stats                       # breakdown + response rate
```

**Manually add an application:**
```bash
./run.sh tracker add --company "Notion" --role "PMM" --url "https://..."
```

**Statuses:** `Saved → Applied → Phone Screen → Interview → Offer / Rejected / Withdrawn`

---

## Open Output Folder

```bash
./run.sh open
```

Opens the `output/` folder in Finder.
