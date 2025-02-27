E-COMET task
================
Current quick start guide:
--------------------------
1. Install poetry (https://python-poetry.org/docs/#installation)
2. Install pre-commit (https://pre-commit.com/#install)
3. Run `poetry install` to install dependencies
4. Run `pre-commit install` to install pre-commit hooks
5. Copy `.env.example` to `.env` and fill in the values
8. Start the backend with `uvicorn main:app --reload --host 0.0.0.0 --port 80 --forwarded-allow-ips='*' --proxy-headers --env-file ../.env`

Task guide:
--------------------------
1. First, second and third tasks are realized in src
2. Fourth task is realized in folder with name 4
