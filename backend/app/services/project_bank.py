"""
Kaggle-style projects: a brief, a dataset or sandbox, and a checklist to grade against.
Learners build outside SkillAlpha and submit a link (GitHub repo, notebook or deployed app)
plus the checklist items they met. Each goal family lists its projects easiest first; the
roadmap places one at the end of each phase.
"""
from typing import Dict, List, Optional

B, I, A = "BEGINNER", "INTERMEDIATE", "ADVANCED"
KG = "https://www.kaggle.com/"


def P(pid, level, title, summary, dataset, dataset_url, hours, brief, rubric):
    return {"id": pid, "level": level, "title": title, "summary": summary, "dataset": dataset,
            "dataset_url": dataset_url, "estimated_hours": hours, "brief": brief, "rubric": rubric}


PROJECT_BANK: Dict[str, List[dict]] = {
    "quant_finance": [
        P("qf-ma-crossover", B, "Moving-average crossover backtest",
          "Your first complete strategy: data in, trades out, honest metrics at the end.",
          "Daily prices from yfinance (any NIFTY 50 or S&P 500 stock)", "https://github.com/ranaroussi/yfinance", 6,
          ["Download at least five years of daily prices", "Create a 50/200-day moving-average signal and shift it by one day",
           "Compute strategy returns with a 0.1% cost per trade", "Report CAGR, Sharpe ratio, maximum drawdown and compare with buy-and-hold"],
          ["The signal is shifted, so there is no look-ahead bias", "Transaction costs are included", "Sharpe ratio and maximum drawdown are reported",
           "An equity curve is plotted against buy-and-hold", "The README states when the strategy fails"]),
        P("qf-pairs", I, "Pairs trading on a cointegrated pair",
          "Find a pair that moves together, trade the spread, and prove it works out of sample.",
          "Daily prices from yfinance for 20-30 stocks in one sector", "https://github.com/ranaroussi/yfinance", 10,
          ["Test all pairs in one sector for cointegration (Engle-Granger)", "Estimate the hedge ratio and build the spread",
           "Trade the z-score: enter beyond 2, exit near 0", "Hold back the last 30% of the data as an out-of-sample test"],
          ["Cointegration test results are shown for the chosen pair", "The hedge ratio is estimated on training data only", "In-sample and out-of-sample results are both reported",
           "Costs are included for both legs", "The README explains what would break the pair"]),
        P("qf-momentum", I, "Cross-sectional momentum portfolio",
          "Rank a universe every month, hold the winners, and measure whether the edge is real.",
          "Monthly prices for 30-50 large-cap stocks from yfinance", "https://github.com/ranaroussi/yfinance", 10,
          ["Compute 12-1 month momentum for every stock each month", "Hold the top 20% equally weighted, rebalance monthly",
           "Compare with an equal-weight benchmark of the whole universe", "Add volatility targeting and report the change"],
          ["Momentum skips the most recent month", "Rebalancing uses only past data", "Turnover and costs are reported",
           "Performance is compared with a benchmark", "Survivorship bias in the universe is discussed"]),
        P("qf-ml-signal", A, "Machine-learning signal with walk-forward validation",
          "Train a model to forecast returns or volatility and backtest it the way it would trade live.",
          "Optiver Realized Volatility Prediction (Kaggle) or your own yfinance features", KG + "competitions/optiver-realized-volatility-prediction", 16,
          ["Engineer at least ten features that use only past data", "Validate with walk-forward splits, never random k-fold",
           "Compare a gradient-boosting model with a simple baseline", "Turn predictions into positions and backtest with costs"],
          ["No feature uses future information", "Validation is walk-forward or purged", "A naive baseline is reported next to the model",
           "Feature importance is shown", "The out-of-sample backtest includes costs"]),
        P("qf-paper-bot", A, "Thirty-day paper-trading bot",
          "Run one of your strategies unattended on a paper account and keep a real track record.",
          "Alpaca paper trading account (free)", "https://docs.alpaca.markets/docs/paper-trading", 20,
          ["Connect to the broker API and place paper orders from code", "Schedule the strategy to run every trading day",
           "Log every signal, order and fill; send yourself an alert on errors", "Add a daily loss limit that stops trading"],
          ["The bot ran on at least 20 trading days", "Every order and fill is logged", "A kill switch or daily loss limit exists",
           "Positions are reconciled with the broker on start-up", "Live results are compared with the backtest"]),
    ],
    "machine_learning": [
        P("ml-titanic", B, "Titanic survival classifier", "The classic first competition: clean data, train, validate, submit.",
          "Titanic - Machine Learning from Disaster", KG + "competitions/titanic", 5,
          ["Explore the data and handle missing values", "Train two different models", "Compare them with 5-fold cross-validation", "Submit predictions to the leaderboard"],
          ["Preprocessing sits inside a Pipeline", "Cross-validated accuracy is reported", "Two models are compared", "A Kaggle submission was made"]),
        P("ml-house-prices", I, "House price regression with engineered features", "Feature engineering and tuning on a messy real dataset.",
          "House Prices - Advanced Regression Techniques", KG + "competitions/house-prices-advanced-regression-techniques", 10,
          ["Build a baseline model first", "Add at least five engineered features", "Tune a gradient-boosting model", "Explain the most important features"],
          ["A baseline score is recorded", "Each new feature's effect on the score is shown", "Tuning used cross-validation, not the test set", "Feature importance is plotted"]),
        P("ml-churn-api", A, "Churn model served as an API", "Take a model all the way to a running, monitored service.",
          "Telco Customer Churn", KG + "datasets/blastchar/telco-customer-churn", 16,
          ["Train and track experiments for a churn model", "Serve it with FastAPI and validate inputs", "Package it with Docker", "Log predictions and write a drift check"],
          ["Experiments are tracked", "The /predict endpoint validates input", "The service runs from a Docker image", "A drift check script exists", "The README has run instructions"]),
    ],
    "data_science": [
        P("ds-eda-story", B, "An EDA story in five charts", "Explore a dataset and tell someone what you found.",
          "Netflix Movies and TV Shows", KG + "datasets/shivamb/netflix-shows", 5,
          ["Clean the data and document each decision", "Explore distributions and relationships", "Pick five findings", "Present each with one chart and a headline"],
          ["Missing data is handled and explained", "Every chart has a title that states the finding", "Axes are labelled", "A short conclusion lists next questions"]),
        P("ds-ab-test", I, "A/B test analysis and recommendation", "Decide whether a new page should launch, and defend the decision.",
          "A/B testing dataset", KG + "datasets/zhangluyuan/ab-testing", 8,
          ["Check the data for mismatched or duplicate users", "State the hypotheses and choose a test", "Compute the p-value, effect size and confidence interval", "Write a one-page recommendation"],
          ["Data quality problems are found and handled", "The test choice is justified", "Effect size and interval are reported, not only a p-value", "The recommendation is clear to a non-analyst"]),
        P("ds-store-sales", A, "Store sales forecasting", "Forecast daily sales for many stores and validate the forecast honestly.",
          "Store Sales - Time Series Forecasting", KG + "competitions/store-sales-time-series-forecasting", 16,
          ["Explore trend, seasonality and holidays", "Build a naive baseline", "Train a model with lag features", "Validate on the most recent weeks"],
          ["Validation respects time order", "A naive baseline is reported", "Lag features use only past data", "Errors are analysed by store or product family"]),
    ],
    "backend": [
        P("be-todo-api", B, "To-do list REST API", "A small API done properly.",
          "No dataset: design your own schema", "https://fastapi.tiangolo.com/tutorial/", 6,
          ["Design the resources and routes", "Implement create, read, update and delete", "Validate input and return correct status codes", "Write tests for each route"],
          ["Status codes are correct (201, 404, 422)", "Input is validated", "Lists are paginated", "Automated tests pass", "API docs are generated"]),
        P("be-auth-bookmarks", I, "Bookmark service with login", "Users, tokens and a real database.",
          "PostgreSQL (local or free tier)", "https://www.postgresql.org/docs/current/tutorial.html", 12,
          ["Add users with hashed passwords", "Issue and verify JWT access tokens", "Scope every query to the logged-in user", "Add an index and show the query plan"],
          ["Passwords use a slow salted hash", "Users cannot read each other's data", "Tokens expire", "An EXPLAIN plan shows the index is used", "Tests cover the auth flow"]),
        P("be-url-shortener", A, "URL shortener that survives load", "Caching, rate limits, async I/O and containers.",
          "No dataset: generate load with a script", "https://docs.docker.com/get-started/", 16,
          ["Build the shorten and redirect endpoints with async handlers", "Add caching for hot links", "Add per-client rate limiting", "Ship with Docker Compose and a load test"],
          ["Redirects are served from cache when possible", "Rate limiting returns 429", "The service starts with one compose command", "Load-test results are in the README"]),
    ],
    "frontend": [
        P("fe-book-search", B, "Book search app", "Fetch, filter and display data from a public API.",
          "Open Library Search API", "https://openlibrary.org/developers/api", 6,
          ["Build a search box and results list", "Show loading, empty and error states", "Add a detail view", "Make it usable on a phone"],
          ["Loading and error states exist", "Search is debounced", "The layout works at phone width", "Components are small and named clearly"]),
        P("fe-typed-dashboard", I, "Typed GitHub dashboard", "TypeScript and server-state caching on a real API.",
          "GitHub REST API", "https://docs.github.com/en/rest", 12,
          ["Model the API responses with TypeScript types", "Fetch with TanStack Query", "Add filters and pagination", "Add one optimistic update"],
          ["Strict mode is on with no any", "Queries are cached with sensible keys", "Pagination works", "Errors are shown to the user"]),
        P("fe-fast-table", A, "Ten-thousand-row table that stays fast", "Measure, fix and prove a performance improvement.",
          "Generate 10,000 rows locally", "https://react.dev/reference/react/memo", 14,
          ["Render the slow version and profile it", "Add virtualization and memoization", "Code-split a heavy route", "Record before and after numbers"],
          ["Profiler screenshots show before and after", "Scrolling stays smooth", "A Lighthouse or Web Vitals report is included", "No unnecessary re-renders remain in the Profiler"]),
    ],
    "data_engineering": [
        P("de-star-schema", B, "Star schema for an online shop", "Turn raw tables into a model analysts can query.",
          "Brazilian E-Commerce Public Dataset by Olist", KG + "datasets/olistbr/brazilian-ecommerce", 8,
          ["Explore the source tables", "Design fact and dimension tables", "Load them with SQL", "Answer five business questions"],
          ["A schema diagram is included", "Facts and dimensions are separated", "Load scripts can be re-run safely", "Five analytical queries are provided"]),
        P("de-spark-taxi", I, "NYC taxi trips with PySpark", "Process data too big for pandas.",
          "NYC TLC Trip Record Data", "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page", 12,
          ["Load several months of Parquet files", "Clean and aggregate by hour and zone", "Join with the zone lookup", "Write partitioned output"],
          ["At least three months are processed", "The job runs from one command", "One shuffle or join was optimized and explained", "Output is partitioned"]),
        P("de-airflow-pipeline", A, "Daily pipeline with Airflow", "Schedule, retry and backfill a real ingestion job.",
          "GH Archive (hourly GitHub events)", "https://www.gharchive.org/", 16,
          ["Write a DAG that downloads, transforms and loads one day", "Make every task idempotent", "Add retries and a data-quality check", "Backfill one week"],
          ["Re-running a day does not duplicate data", "A data-quality task can fail the run", "A one-week backfill succeeded", "The DAG is documented"]),
    ],
    "devops": [
        P("do-containerize", B, "Containerize an app with its database", "One command to run everything.",
          "Any small web app you wrote", "https://docs.docker.com/get-started/", 6,
          ["Write a small Dockerfile", "Add a database with Compose", "Use a volume for data", "Document how to run it"],
          ["The image builds from a clean clone", "docker compose up starts everything", "Data survives a restart", "No secrets are in the image"]),
        P("do-ci-pipeline", I, "CI/CD pipeline for a repository", "Every push is tested, built and ready to ship.",
          "One of your GitHub repositories", "https://docs.github.com/en/actions", 10,
          ["Run tests and linting on every push", "Build and push a Docker image", "Deploy on merges to main", "Protect the main branch"],
          ["A failing test blocks the merge", "Images are tagged with the commit", "Secrets are stored in the CI system", "A deployment happens without manual steps"]),
        P("do-k8s-terraform", A, "Kubernetes deployment defined as code", "Infrastructure and rollout you can recreate from scratch.",
          "A local cluster (kind or minikube)", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", 16,
          ["Describe the infrastructure with Terraform", "Deploy the app with a Deployment and Service", "Add probes and resource limits", "Do a rolling update and a rollback"],
          ["terraform apply creates the environment", "Readiness and liveness probes exist", "A rolling update finished with no downtime", "A rollback was demonstrated"]),
    ],
    "security": [
        P("se-bandit", B, "OverTheWire Bandit write-up", "Learn the shell by breaking into the next level.",
          "OverTheWire: Bandit", "https://overthewire.org/wargames/bandit/", 8,
          ["Solve levels 0 to 15", "Record the command that solved each level", "Explain why it worked"],
          ["At least 15 levels are solved", "Each level has an explanation, not just a command", "No passwords are published"]),
        P("se-juice-shop-audit", I, "Security audit of OWASP Juice Shop", "A real test with a real report, on a target you are allowed to attack.",
          "OWASP Juice Shop (run locally)", "https://owasp.org/projects/juice-shop", 14,
          ["Run Juice Shop on your own machine", "Find issues in at least three OWASP Top 10 categories", "Rate each by risk", "Write a report with fixes"],
          ["Testing was done only on your local instance", "At least five findings are documented", "Each finding has steps to reproduce", "Each finding has a recommended fix"]),
        P("se-harden-app", A, "Break it, then fix it", "Exploit a vulnerable app and patch each hole.",
          "Damn Vulnerable Web Application (run locally)", "https://github.com/digininja/DVWA", 16,
          ["Exploit SQL injection, XSS and broken access control locally", "Patch each vulnerability in the code", "Show the exploit no longer works", "Write a short threat model"],
          ["Three vulnerability classes were exploited locally", "Each has a code fix", "Each fix was re-tested", "A threat model lists remaining risks"]),
    ],
    "mobile": [
        P("mo-list-detail", B, "List and detail app", "Two screens, real data, smooth scrolling.",
          "PokeAPI", "https://pokeapi.co/", 8,
          ["Fetch a paged list", "Render it lazily", "Add a detail screen", "Handle loading and errors"],
          ["The list scrolls smoothly", "Navigation works both ways", "Loading and error states exist", "It runs on a phone or emulator"]),
        P("mo-offline-notes", I, "Offline-first notes app", "Shared state and local persistence.",
          "No dataset: store notes on the device", "https://reactnative.dev/docs/getting-started", 12,
          ["Create, edit and delete notes", "Keep state in one shared store", "Persist notes on the device", "Sync the list and detail screens"],
          ["Notes survive an app restart", "Both screens update when a note changes", "State lives in one store", "The app works with no network"]),
        P("mo-photo-journal", A, "Photo journal with camera and location", "Device features, permissions and secure storage.",
          "No dataset: your own photos", "https://docs.expo.dev/versions/latest/", 16,
          ["Take photos in the app", "Tag each with location", "Ask for permissions at the right moment", "Protect the journal with a stored login token"],
          ["Permissions are requested in context", "Denied permissions are handled gracefully", "The token is in secure storage", "Photos and locations are shown together"]),
    ],
    "general": [
        P("ge-cli-tool", B, "Command-line tool with tests", "A small, well-structured program.",
          "No dataset: choose a task you repeat by hand", "https://docs.python.org/3/tutorial/", 6,
          ["Pick a repetitive task and automate it", "Split the code into functions and modules", "Write tests", "Write a README"],
          ["The tool has a help message", "Logic is separated from input and output", "Tests pass", "The README shows example usage"]),
        P("ge-api-service", I, "Service built on a third-party API", "Integrate someone else's API safely.",
          "Public APIs list", "https://github.com/public-apis/public-apis", 10,
          ["Choose an API and read its limits", "Wrap it in your own endpoint", "Handle errors, timeouts and rate limits", "Keep secrets out of the code"],
          ["Secrets come from environment variables", "Timeouts and retries are implemented", "Rate limits are respected", "Input is validated"]),
        P("ge-deploy-app", A, "Deployed app with a pipeline", "From repository to a public URL, automatically.",
          "One of your own apps", "https://docs.github.com/en/actions", 14,
          ["Containerize the app", "Add a pipeline that tests and deploys", "Add a health check", "Demonstrate a rollback"],
          ["The app is reachable at a public URL", "Deploys happen from the pipeline", "A health check exists", "A rollback was performed and documented"]),
    ],
}

_BY_ID: Dict[str, dict] = {}
_FAMILY_OF: Dict[str, str] = {}
for _family, _items in PROJECT_BANK.items():
    for _p in _items:
        assert _p["id"] not in _BY_ID, _p["id"]
        _BY_ID[_p["id"]] = _p
        _FAMILY_OF[_p["id"]] = _family


def get_project(project_id: str) -> Optional[dict]:
    return _BY_ID.get(project_id)


def family_of(project_id: str) -> Optional[str]:
    return _FAMILY_OF.get(project_id)


def projects_for_family(family: str) -> List[dict]:
    return PROJECT_BANK.get(family, PROJECT_BANK["general"])


def projects_for_phases(family: str, phase_count: int) -> List[Optional[dict]]:
    """One project per phase, easiest first; early phases get none when there are more phases than projects."""
    projects = projects_for_family(family)
    if phase_count <= 0:
        return []
    if len(projects) >= phase_count:
        step = (len(projects) - 1) / (phase_count - 1) if phase_count > 1 else 0
        return [projects[round(i * step)] if phase_count > 1 else projects[0] for i in range(phase_count)]
    return [None] * (phase_count - len(projects)) + projects
