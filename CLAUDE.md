# Phishing Guard and Coach — standing rules

- The tutorial notebook in this folder is the source of truth for the
  openai-agents 0.22.0 API. If it differs from your memory, follow the
  tutorial.
- Read OPENAI_API_KEY from the environment through python-dotenv, with a
  getpass fallback in notebooks. Never print or open .env.
- Never edit data/test_cases.json or score_case to raise a score without
  asking me first.
- Ask before running any command that calls the OpenAI API.
- Build one day's checklist from PLAN.md at a time, then stop and show me
  the end-of-day check.
- Put logic in .py files. Keep notebooks as thin layers that import them.
