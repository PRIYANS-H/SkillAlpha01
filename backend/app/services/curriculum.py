"""
Day-by-day study plans.

SKILL_GUIDE holds, for every skill, the three things a learner should focus on, one concrete
thing to build, and one question they should be able to answer afterwards. build_day_plan
turns that into dated study days (learn -> practice -> build -> review) sized to the learner's gap.
"""
from typing import Dict, List, Optional, Tuple

# skill name -> (focus topics, build task, self-check question)
SKILL_GUIDE: Dict[str, Tuple[Tuple[str, str, str], str, str]] = {
    # ---------- Programming & data foundations ----------
    "Python Architecture": (("Functions, classes and modules", "Lists, dicts, sets and when each is fast", "Iterators, generators and comprehensions"),
        "Write a small command-line expense tracker with a class, a JSON file for storage and three functions you test by hand.",
        "Why is a mutable default argument such as def f(x=[]) a bug waiting to happen?"),
    "SQL & Analytical Queries": (("SELECT, WHERE, GROUP BY and HAVING", "INNER and LEFT joins", "Window functions: ROW_NUMBER, LAG, running totals"),
        "Load any CSV into SQLite and answer five business questions with SQL, including one that needs a window function.",
        "What is the difference between WHERE and HAVING?"),
    "Applied Statistics": (("Mean, variance and common distributions", "Sampling and the central limit theorem", "Confidence intervals and p-values"),
        "Simulate 10,000 sample means in Python and plot how their spread shrinks as the sample size grows.",
        "What does a 95% confidence interval actually claim?"),
    "Pandas & Data Manipulation": (("Loading, filtering and selecting with loc/iloc", "groupby, merge and pivot", "Handling missing values and dtypes"),
        "Clean a messy public dataset: fix types, handle missing values, and produce three grouped summary tables.",
        "When do you use merge and when do you use concat?"),
    "Machine Learning Foundations": (("Supervised vs unsupervised learning", "Bias-variance trade-off and overfitting", "Linear models and decision trees"),
        "Train a logistic regression and a decision tree on the Titanic data and compare their validation accuracy.",
        "How can you tell from train and validation scores that a model is overfitting?"),
    "Model Validation & Split Hygiene": (("Train, validation and test splits", "k-fold and stratified cross-validation", "Target leakage and pipelines"),
        "Rebuild one of your models inside a scikit-learn Pipeline and report a 5-fold cross-validated score.",
        "Why must a scaler be fitted on the training fold only?"),
    "Feature Engineering & Selection": (("Scaling and encoding categorical data", "Creating features from dates, text and groups", "Feature importance and selection"),
        "Add five engineered features to a tabular model and show which ones improve the cross-validated score.",
        "When is target encoding risky, and how do you make it safe?"),
    "Hyperparameter Optimization": (("Grid, random and Bayesian search", "Search spaces and early stopping", "Nested validation to avoid tuning on the test set"),
        "Tune a gradient boosting model with Optuna (30 trials) and compare it with the default settings on a held-out set.",
        "Why does random search usually beat grid search with the same budget?"),
    "Model Deployment & APIs": (("Saving and loading models", "A prediction endpoint with input validation", "Packaging the service in a container"),
        "Serve one of your models with FastAPI: a /predict endpoint, pydantic validation and a Dockerfile.",
        "What should a prediction API do when it receives a field it has never seen?"),
    "Docker & Containerization": (("Images, containers and layers", "Writing a small, cache-friendly Dockerfile", "Compose, volumes and networks"),
        "Containerize an app you wrote, then run it together with a database using docker compose.",
        "Why should dependency installation come before copying your source code in a Dockerfile?"),
    "MLOps & Monitoring": (("Experiment tracking and model registry", "Data and concept drift", "Automated retraining and alerts"),
        "Track three training runs in MLflow and write a script that flags drift between two months of input data.",
        "What is the difference between data drift and concept drift?"),
    "Exploratory Data Analysis": (("Distributions, outliers and missing data", "Relationships between variables", "Turning observations into questions"),
        "Write an EDA notebook on a Kaggle dataset that ends with five findings, each backed by one chart.",
        "Why can a correlation be misleading without a scatter plot?"),
    "Applied Statistics & Hypothesis Testing": (("Null and alternative hypotheses", "t-tests, chi-square tests and p-values", "Effect size, power and multiple testing"),
        "Analyse an A/B test dataset: choose the test, compute the p-value and effect size, and write a one-paragraph decision.",
        "Why is a statistically significant result not always an important one?"),
    "Data Visualization & Storytelling": (("Choosing the right chart", "Decluttering: labels, colour and scale", "Ordering charts into a narrative"),
        "Turn one analysis into a five-chart story with a headline above each chart that states the finding.",
        "When is a bar chart better than a pie chart?"),
    # ---------- Backend ----------
    "RESTful API Architecture": (("Resources, verbs and status codes", "Validation, pagination and errors", "Versioning and idempotency"),
        "Build a CRUD API for a to-do list with FastAPI, correct status codes, pagination and automatic docs.",
        "Which HTTP methods must be idempotent, and why does that matter for retries?"),
    "Database Indexing & ORM Hygiene": (("How B-tree indexes speed up queries", "Reading EXPLAIN output", "The N+1 query problem and eager loading"),
        "Create a table with 1 million rows, measure a slow query, add an index and record the before/after plans.",
        "Why can an index make writes slower?"),
    "Authentication & JWT Security": (("Sessions versus tokens", "JWT structure, signing and expiry", "Password hashing and OAuth 2.0 flows"),
        "Add login to your API: hashed passwords, short-lived access tokens and a protected route.",
        "Why must a server verify a JWT's signature and not only decode it?"),
    "Async Programming & Concurrency": (("The event loop, coroutines and await", "Running tasks concurrently with gather", "CPU-bound vs I/O-bound work"),
        "Write a script that fetches 50 URLs sequentially and then concurrently with asyncio, and compare the timings.",
        "What happens to an async server when one handler calls time.sleep()?"),
    # ---------- Frontend ----------
    "JavaScript Fundamentals & ES6+": (("Scope, closures and this", "Array methods, destructuring and spread", "Promises and async/await"),
        "Build a page that fetches data from a public API and renders a filterable list using plain JavaScript.",
        "What is a closure, and where have you used one without noticing?"),
    "React Component Architecture": (("Components, props and state", "Lifting state up and composition", "Effects and when not to use them"),
        "Build a small React app with at least four components, lifted state and a controlled form.",
        "Why should state live in the closest common parent of the components that use it?"),
    "TypeScript Integration": (("Basic types, interfaces and unions", "Generics and utility types", "Typing props, hooks and events"),
        "Convert one of your JavaScript projects to TypeScript with strict mode on and no use of any.",
        "What is the difference between unknown and any?"),
    "State Management & React Query": (("Server state versus client state", "Queries, cache keys and invalidation", "Mutations and optimistic updates"),
        "Replace hand-written fetch-in-useEffect code with TanStack Query, including one optimistic mutation.",
        "What does invalidating a query key do?"),
    "Performance Optimization & Memoization": (("Finding re-renders with the Profiler", "memo, useMemo and useCallback", "Code splitting and list virtualization"),
        "Profile a slow list, fix it with memoization or virtualization, and record the before/after render times.",
        "Why can wrapping everything in useMemo make an app slower?"),
    # ---------- Data engineering ----------
    "Data Modeling & Warehousing": (("Facts, dimensions and star schemas", "Normalization versus denormalization", "Slowly changing dimensions"),
        "Design a star schema for an online shop and load sample data into it with SQL.",
        "Why are star schemas denormalized on purpose?"),
    "Apache Spark & Distributed Computing": (("DataFrames and lazy evaluation", "Partitions, shuffles and joins", "Reading the Spark UI"),
        "Process a multi-gigabyte public dataset with PySpark and explain one shuffle you removed or reduced.",
        "What is the difference between a transformation and an action?"),
    "Orchestration & Airflow": (("DAGs, tasks and operators", "Scheduling, retries and backfills", "Idempotent tasks"),
        "Write an Airflow DAG with three dependent tasks that downloads, transforms and loads a daily file.",
        "Why must a task be safe to run twice?"),
    # ---------- DevOps ----------
    "Linux Systems & Shell Scripting": (("Files, permissions and processes", "Pipes, grep, sed and awk", "Bash scripts with variables and loops"),
        "Write a bash script that backs up a folder, rotates old backups and logs what it did.",
        "What does chmod 750 allow, and for whom?"),
    "Kubernetes Orchestration": (("Pods, Deployments and Services", "ConfigMaps, Secrets and probes", "Rolling updates and scaling"),
        "Deploy your containerized app to a local cluster with a Deployment, a Service and a readiness probe.",
        "What is the difference between a liveness and a readiness probe?"),
    "Infrastructure as Code & Terraform": (("Providers, resources and state", "Variables, outputs and modules", "plan, apply and remote state"),
        "Describe a small cloud setup in Terraform, review the plan, apply it and destroy it again.",
        "Why should the Terraform state file never be edited by hand or committed to git?"),
    "CI/CD Pipeline Automation": (("Workflows, jobs and steps", "Running tests and builds on every push", "Secrets, environments and deployments"),
        "Add a GitHub Actions workflow to one of your repositories that runs tests and builds a Docker image on each push.",
        "Why should a pipeline fail fast?"),
    # ---------- Security ----------
    "Network Fundamentals & Security": (("IP, TCP, UDP and ports", "DNS and HTTP/TLS", "Firewalls and network segmentation"),
        "Capture your own traffic with Wireshark and identify a DNS lookup, a TCP handshake and a TLS handshake.",
        "What happens, step by step, when you type a URL and press Enter?"),
    "Web Security & OWASP Top 10": (("Injection and cross-site scripting", "Broken access control", "Security misconfiguration"),
        "Solve five PortSwigger labs from three different vulnerability classes and write up how each one is prevented.",
        "Why do parameterized queries stop SQL injection?"),
    "Cryptography & Identity Hygiene": (("Hashing versus encryption", "Symmetric and public-key cryptography", "TLS, certificates and password storage"),
        "Write a script that hashes passwords with a slow salted algorithm and verifies them, then explain each parameter.",
        "Why is SHA-256 on its own a poor way to store passwords?"),
    "Penetration Testing & Auditing": (("Scope, rules of engagement and reconnaissance", "Scanning and exploitation", "Reporting findings by risk"),
        "Run a full test against OWASP Juice Shop on your own machine and write a report with three findings and fixes.",
        "What must be agreed in writing before a penetration test begins?"),
    # ---------- Mobile ----------
    "Mobile UI Architecture": (("Layouts, lists and navigation", "Component or widget trees", "Adapting to screen sizes"),
        "Build a two-screen app with a scrolling list, a detail screen and navigation between them.",
        "Why should long lists be rendered lazily?"),
    "State Management & Reactivity": (("Local versus shared state", "Unidirectional data flow", "Stores, providers and side effects"),
        "Add a shared store to your app so two screens stay in sync when data changes.",
        "What goes wrong when two screens each keep their own copy of the same data?"),
    "REST & GraphQL Integration": (("Calling REST endpoints and parsing JSON", "GraphQL queries and mutations", "Loading, error and offline states"),
        "Connect your app to a public API with loading and error states and a pull-to-refresh.",
        "What problem does GraphQL solve that REST does not?"),
    "Native Device Access & Security": (("Runtime permissions", "Camera, location and secure storage", "Mobile threats from the OWASP Mobile Top 10"),
        "Add one device feature (camera or location) with a proper permission flow and store a token in secure storage.",
        "Why should tokens not be stored in plain local storage on a phone?"),
    # ---------- General software ----------
    "Software Architecture": (("Coupling, cohesion and layers", "Common design patterns", "Trade-offs: monolith versus services"),
        "Draw the architecture of an app you built, then refactor one tangled module behind a clear interface.",
        "What does loose coupling buy you when requirements change?"),
    "API Integration & Web Security": (("Calling third-party APIs safely", "API keys, OAuth and rate limits", "CORS and input validation"),
        "Integrate one third-party API with retries, rate-limit handling and secrets kept out of the code.",
        "Why should API keys never be shipped in front-end code?"),
    "Deployment & CI/CD Pipelines": (("Environments and configuration", "Automated build, test and deploy", "Rollbacks and health checks"),
        "Deploy an app to a free host with a pipeline that tests before deploying and can be rolled back.",
        "What makes a deployment safe to roll back?"),
    # ---------- Quant finance ----------
    "Python for Quant Finance": (("NumPy arrays and vectorized maths", "pandas time series: resample, shift, rolling", "Downloading price data with yfinance"),
        "Download five years of daily prices for five stocks, compute daily and cumulative returns, and plot them on one chart.",
        "How do you compute daily returns from a price Series in one line?"),
    "Probability & Statistics for Trading": (("Expected value, variance and Bayes' rule", "The normal distribution and fat tails", "Hypothesis tests on returns"),
        "Test whether a stock's mean daily return differs from zero, and compare its return histogram with a normal curve.",
        "Why does volatility scale with the square root of time?"),
    "Financial Markets & Instruments": (("Stocks, futures and options", "Order books, bid/ask spread and order types", "Alpha, beta and benchmarks"),
        "Write a one-page note that follows one trade from order to settlement on NSE, including every cost you pay.",
        "What is the difference between a market order and a limit order?"),
    "Backtesting & Performance Metrics": (("Signals, positions and shifting to avoid look-ahead", "Sharpe ratio, drawdown and win rate", "Transaction costs and out-of-sample tests"),
        "Backtest a moving-average crossover with costs, and report CAGR, Sharpe ratio and maximum drawdown in a table.",
        "Why must a signal be shifted by one bar before it is traded?"),
    "Time Series Analysis & Stationarity": (("Stationarity and the ADF test", "Autocorrelation: ACF and PACF", "Rolling statistics and z-scores"),
        "Run the ADF test on prices and on returns for three stocks, plot their ACF, and explain the difference.",
        "What does it mean when the ADF test fails to reject its null hypothesis?"),
    "Mean Reversion & Pairs Trading": (("Cointegration and the Engle-Granger test", "Hedge ratio, spread and z-score", "Entry, exit and stop rules"),
        "Find one cointegrated pair, build its spread and backtest a z-score strategy with costs and an out-of-sample period.",
        "Why is high correlation not enough to trade a pair?"),
    "Momentum & Technical Signals": (("Time-series and cross-sectional momentum", "RSI, MACD and moving averages", "Volatility-based position sizing"),
        "Rank 30 stocks by 12-month momentum each month, hold the top five, and compare the result with the index.",
        "What is the difference between time-series momentum and cross-sectional momentum?"),
    "Machine Learning for Trading": (("Features and labels without leakage", "Walk-forward validation", "Random forests and gradient boosting on returns"),
        "Train a model to predict next-day direction with walk-forward validation, then backtest its signals with costs.",
        "Why is random k-fold cross-validation wrong for time series?"),
    "Risk Management & Portfolio Construction": (("Volatility, correlation and diversification", "Value at Risk and drawdown limits", "Position sizing and mean-variance optimization"),
        "Build a five-asset portfolio three ways (equal weight, minimum variance, maximum Sharpe) and compare risk and return.",
        "What does a 1-day 95% VaR tell you, and what does it hide?"),
    "Live Trading & Broker APIs": (("Broker APIs, order types and order states", "Paper trading and logging", "Kill switches and reconciliation"),
        "Run one of your strategies on a paper-trading account for a week with logging, an alert and a daily loss limit.",
        "What should a bot do first after it reconnects to the broker?"),
    "Options Pricing & Greeks": (("Payoffs and put-call parity", "Black-Scholes and implied volatility", "Delta, gamma, theta and vega"),
        "Code the Black-Scholes price and Greeks for a call and a put, then compute implied volatility from a market price.",
        "Why does an option lose value as time passes, all else equal?"),
    "Alpha Research & Factor Models": (("Factor returns and the Fama-French model", "Information coefficient and turnover", "Avoiding data snooping"),
        "Build one factor (for example value or momentum), compute its monthly IC and quintile returns, and write up the result.",
        "Why does testing many signals inflate the best backtest?"),
    "Quant Interview Problem Solving": (("Expected value and conditional probability puzzles", "Mental maths under time pressure", "Explaining a strategy clearly"),
        "Solve 20 timed probability puzzles, then record a 90-second explanation of your best strategy and its weaknesses.",
        "What is the expected number of coin flips needed to see two heads in a row?"),
}

GENERIC_GUIDE = (("The core concepts and vocabulary", "The most common patterns in real projects", "Typical mistakes and how to avoid them"),
                 "Build a small project that uses this skill end to end and publish it on GitHub.",
                 "Could you explain the main idea to a friend in two minutes?")

FULL_PLAN = ("LEARN", "PRACTICE", "BUILD", "REVIEW")
REINFORCE_PLAN = ("PRACTICE", "BUILD", "REVIEW")


def get_guide(skill_name: str):
    return SKILL_GUIDE.get(skill_name, GENERIC_GUIDE)


def build_day_plan(skill_name: str, status: str, primary_resource: Optional[str] = None,
                   problem_count: int = 0) -> List[Dict]:
    """
    Study days for one skill. A skill the learner is missing gets four days
    (learn, practice, build, review); one that only needs reinforcement skips the
    separate learning day. Each day has numbered steps, like a page of a study guide.
    """
    topics, build, check = get_guide(skill_name)
    source = primary_resource or "the first resource listed for this task"
    kinds = REINFORCE_PLAN if status == "NEEDS_REINFORCEMENT" else FULL_PLAN
    practice_line = (
        f"Open Practice and work through the {problem_count} problems for {skill_name}, easiest first"
        if problem_count else f"Do the hands-on exercises in the practice resource for {skill_name}"
    )
    days = {
        "LEARN": {
            "title": "Learn the core ideas",
            "steps": [f"Study: {source}"] + [f"Focus on: {t}" for t in topics] + ["Write five lines of notes in your own words"],
            "check": check,
        },
        "PRACTICE": {
            "title": "Practice problems",
            "steps": ([f"Skim: {source} (you already know part of this)"] if "LEARN" not in kinds else []) + [
                practice_line,
                "For every miss, read the explanation and try a similar problem",
                "Finish with one of the linked outside problems",
            ],
            "check": None,
        },
        "BUILD": {
            "title": "Build it",
            "steps": [build, "Push the code to GitHub with a short README", "Write down the one thing that was harder than expected"],
            "check": None,
        },
        "REVIEW": {
            "title": "Review and skill check",
            "steps": ["Explain the three focus topics out loud without notes", "Take the quick skill check on this task (pass = 2 of 3)",
                      "Rate your confidence honestly and complete the task"],
            "check": check,
        },
    }
    return [{"kind": k, **days[k]} for k in kinds]
