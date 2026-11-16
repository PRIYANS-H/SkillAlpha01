"""
Curated resource library: hand-picked videos, courses, docs, practice sites and books for
every skill in skill_service.GOAL_SKILL_GRAPHS.

Each entry: (title, url, provider, resource_type, duration_minutes, difficulty, skills, why).
`why` is shown to learners as the reason the resource is on their plan.
`sync_resource_library` upserts by URL, so it is safe to run on every startup and new
entries reach databases that were seeded before they existed.
"""
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

from app.models.models import Resource, ResourceSkill, Skill
from app.services.skill_service import GOAL_SKILL_GRAPHS, get_or_create_skill

B, I, A = "BEGINNER", "INTERMEDIATE", "ADVANCED"
VIDEO, DOC, COURSE, PRACTICE, ARTICLE, TUTORIAL, GITHUB, BOOK = (
    "VIDEO", "DOCUMENTATION", "COURSE", "PRACTICE", "ARTICLE", "TUTORIAL", "GITHUB", "BOOK"
)


def Y(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def PL(playlist_id: str) -> str:
    return f"https://www.youtube.com/playlist?list={playlist_id}"


def BK(query: str) -> str:
    """Books link to an Open Library search, never to a download or a shop."""
    return "https://openlibrary.org/search?q=" + query.replace(" ", "+")


# Skill name shorthands (must match skill_service exactly)
PY, SQL, STAT, PANDAS = "Python Architecture", "SQL & Analytical Queries", "Applied Statistics", "Pandas & Data Manipulation"
MLF, MV, FE, HPO = "Machine Learning Foundations", "Model Validation & Split Hygiene", "Feature Engineering & Selection", "Hyperparameter Optimization"
DEPLOY, DOCKER, MLOPS = "Model Deployment & APIs", "Docker & Containerization", "MLOps & Monitoring"
EDA, STATH, VIZ = "Exploratory Data Analysis", "Applied Statistics & Hypothesis Testing", "Data Visualization & Storytelling"
REST, DBIDX, AUTH, ASYNC = "RESTful API Architecture", "Database Indexing & ORM Hygiene", "Authentication & JWT Security", "Async Programming & Concurrency"
JS, REACT, TS, RQ, PERF = "JavaScript Fundamentals & ES6+", "React Component Architecture", "TypeScript Integration", "State Management & React Query", "Performance Optimization & Memoization"
DM, SPARK, AIRFLOW = "Data Modeling & Warehousing", "Apache Spark & Distributed Computing", "Orchestration & Airflow"
LINUX, K8S, TF, CICD = "Linux Systems & Shell Scripting", "Kubernetes Orchestration", "Infrastructure as Code & Terraform", "CI/CD Pipeline Automation"
NET, WEBSEC, CRYPTO, PENTEST = "Network Fundamentals & Security", "Web Security & OWASP Top 10", "Cryptography & Identity Hygiene", "Penetration Testing & Auditing"
MUI, MSTATE, MAPI, MNATIVE = "Mobile UI Architecture", "State Management & Reactivity", "REST & GraphQL Integration", "Native Device Access & Security"
ARCH, APISEC, DEPCI = "Software Architecture", "API Integration & Web Security", "Deployment & CI/CD Pipelines"
QPY, QSTAT, QMKT, QBT = "Python for Quant Finance", "Probability & Statistics for Trading", "Financial Markets & Instruments", "Backtesting & Performance Metrics"
QTS, QMR, QMOM, QML = "Time Series Analysis & Stationarity", "Mean Reversion & Pairs Trading", "Momentum & Technical Signals", "Machine Learning for Trading"
QRISK, QLIVE, QOPT, QALPHA, QINT = "Risk Management & Portfolio Construction", "Live Trading & Broker APIs", "Options Pricing & Greeks", "Alpha Research & Factor Models", "Quant Interview Problem Solving"

Entry = Tuple[str, str, str, str, int, str, List[str], str]

RESOURCE_LIBRARY: List[Entry] = [
    # ---------------- Python ----------------
    ("Learn Python - Full Course for Beginners", Y("rfscVS0vtbw"), "freeCodeCamp", VIDEO, 266, B, [PY, QPY], "One video that covers all core syntax from zero."),
    ("Python OOP Tutorial 1: Classes and Instances", Y("ZDa-Z5JzLYM"), "Corey Schafer", VIDEO, 15, I, [PY], "Clear first look at classes, the base of larger programs."),
    ("Python Tutorial: Generators", Y("bD05uGo_sVI"), "Corey Schafer", VIDEO, 11, I, [PY], "Explains lazy iteration, a common interview and performance topic."),
    ("The Python Tutorial", "https://docs.python.org/3/tutorial/", "Python Docs", DOC, 120, B, [PY, QPY], "The official tour of the language; use it as your reference."),
    ("Exercism Python track", "https://exercism.org/tracks/python", "Exercism", PRACTICE, 90, B, [PY], "Small graded exercises with mentor feedback."),
    ("Kaggle Learn: Python", "https://www.kaggle.com/learn/python", "Kaggle", PRACTICE, 300, B, [PY, QPY], "Short lessons with in-browser exercises."),
    # ---------------- SQL ----------------
    ("SQL Tutorial - Full Database Course for Beginners", Y("HXV3zeQKqGY"), "freeCodeCamp", VIDEO, 260, B, [SQL], "Covers queries, joins and schema design in one sitting."),
    ("SQLBolt interactive lessons", "https://sqlbolt.com/", "SQLBolt", PRACTICE, 90, B, [SQL], "Type queries in the browser and see results immediately."),
    ("PostgreSQL Tutorial: Window Functions", "https://www.postgresql.org/docs/current/tutorial-window.html", "PostgreSQL Docs", DOC, 20, I, [SQL], "Official explanation of the feature analysts use most."),
    ("The SQL Tutorial for Data Analysis", "https://www.thoughtspot.com/sql-tutorial", "ThoughtSpot (Mode)", TUTORIAL, 180, B, [SQL], "Analyst-focused path from SELECT to window functions."),
    ("PostgreSQL Exercises", "https://pgexercises.com/", "pgexercises", PRACTICE, 120, I, [SQL, DBIDX], "Graded exercises on one realistic schema."),
    ("Kaggle Learn: Advanced SQL", "https://www.kaggle.com/learn/advanced-sql", "Kaggle", PRACTICE, 240, I, [SQL, DM], "Joins, analytic functions and nested data on BigQuery."),
    # ---------------- Statistics ----------------
    ("Statistics Fundamentals playlist", PL("PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9"), "StatQuest", VIDEO, 300, B, [STAT, STATH, QSTAT], "Short visual videos, one concept each."),
    ("p-values: What they are and how to interpret them", Y("vemZtEM63GY"), "StatQuest", VIDEO, 11, I, [STAT, STATH, QSTAT], "Fixes the most common misreading of test results."),
    ("Hypothesis Testing and The Null Hypothesis", Y("0oc49DyA3hU"), "StatQuest", VIDEO, 14, I, [STAT, STATH], "The logic behind every A/B test and backtest check."),
    ("Khan Academy: Statistics and Probability", "https://www.khanacademy.org/math/statistics-probability", "Khan Academy", COURSE, 600, B, [STAT, STATH, QSTAT], "Free course with practice questions after each unit."),
    ("Seeing Theory: a visual introduction to probability", "https://seeing-theory.brown.edu/", "Brown University", TUTORIAL, 90, B, [STAT, STATH, QSTAT], "Interactive pictures that build intuition quickly."),
    ("OpenIntro Statistics (free textbook)", "https://www.openintro.org/book/os/", "OpenIntro", ARTICLE, 600, B, [STAT, STATH], "A free, readable textbook with exercises."),
    ("SciPy statistical functions reference", "https://docs.scipy.org/doc/scipy/reference/stats.html", "SciPy Docs", DOC, 30, I, [STATH, QSTAT], "The functions you will call for tests and distributions."),
    ("Statistics 110: Probability (full lecture course)", PL("PL2SOU6wwxB0uwwH80KTQ6ht66KWxbzTIo"), "Harvard", VIDEO, 1700, I, [QSTAT, QINT], "The probability course most quant interviewers assume."),
    ("Bayes theorem, the geometry of changing beliefs", Y("HZGCoVF3YvM"), "3Blue1Brown", VIDEO, 15, B, [QSTAT, QINT, STAT], "A picture of Bayes you will not forget."),
    ("But what is the Central Limit Theorem?", Y("zeJD6dqJ5lo"), "3Blue1Brown", VIDEO, 31, B, [QSTAT, STAT], "Why averages look normal, and when they do not."),
    # ---------------- Pandas / EDA / Viz ----------------
    ("Complete Python Pandas Data Science Tutorial", Y("vmEHCJofslg"), "Keith Galli", VIDEO, 60, B, [PANDAS, QPY], "Fast hands-on tour of loading, filtering and grouping."),
    ("Pandas Tutorials playlist", PL("PL-osiE80TeTsWmV9i9c58mdDCSskIFdDS"), "Corey Schafer", VIDEO, 300, B, [PANDAS, EDA], "Step-by-step series on a real survey dataset."),
    ("10 minutes to pandas", "https://pandas.pydata.org/docs/user_guide/10min.html", "pandas Docs", DOC, 20, B, [PANDAS, QPY], "Official quick tour of the core API."),
    ("Kaggle Learn: Pandas", "https://www.kaggle.com/learn/pandas", "Kaggle", PRACTICE, 240, B, [PANDAS, EDA], "Exercises graded in the browser."),
    ("pandas: Time series / date functionality", "https://pandas.pydata.org/docs/user_guide/timeseries.html", "pandas Docs", DOC, 45, I, [QPY, QTS], "Resampling, shifting and rolling windows for price data."),
    ("Exploratory Data Analysis with Pandas Python", Y("xi0vhXFPegw"), "Rob Mulla", VIDEO, 40, B, [EDA], "A complete EDA on one dataset, start to finish."),
    ("Data Analysis with Python - Full Course", Y("r-uOLxNrNk8"), "freeCodeCamp", VIDEO, 280, B, [EDA, PANDAS], "NumPy, pandas and plotting in one course."),
    ("Kaggle Learn: Data Cleaning", "https://www.kaggle.com/learn/data-cleaning", "Kaggle", PRACTICE, 240, B, [EDA], "Missing values, scaling and parsing dates with exercises."),
    ("Matplotlib Crash Course", Y("3Xc3CA655Y4"), "freeCodeCamp", VIDEO, 90, B, [VIZ], "Everything needed to produce clean charts."),
    ("Kaggle Learn: Data Visualization", "https://www.kaggle.com/learn/data-visualization", "Kaggle", PRACTICE, 240, B, [VIZ, EDA], "Choose and build the right chart, with graded exercises."),
    ("seaborn tutorial", "https://seaborn.pydata.org/tutorial.html", "seaborn Docs", DOC, 60, I, [VIZ], "Statistical charts in a few lines."),
    ("Fundamentals of Data Visualization (free book)", "https://clauswilke.com/dataviz/", "Claus Wilke", ARTICLE, 300, I, [VIZ], "The principles behind charts people understand."),
    # ---------------- Machine learning ----------------
    ("Machine Learning for Everybody", Y("i_LwzRVP7bg"), "freeCodeCamp", VIDEO, 234, B, [MLF], "Core algorithms explained and coded from scratch."),
    ("Machine Learning playlist", PL("PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF"), "StatQuest", VIDEO, 600, B, [MLF], "Each algorithm in a short visual video."),
    ("Machine Learning Fundamentals: Bias and Variance", Y("EuBBz3bI-aA"), "StatQuest", VIDEO, 7, B, [MLF, MV], "The trade-off behind overfitting."),
    ("Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course", "Google", COURSE, 900, B, [MLF], "Free course with interactive exercises."),
    ("Kaggle Learn: Intro to Machine Learning", "https://www.kaggle.com/learn/intro-to-machine-learning", "Kaggle", PRACTICE, 180, B, [MLF], "Train and validate your first models in the browser."),
    ("scikit-learn User Guide: Supervised learning", "https://scikit-learn.org/stable/supervised_learning.html", "scikit-learn Docs", DOC, 90, I, [MLF], "Reference for every model you will use."),
    ("scikit-learn: Cross-validation", "https://scikit-learn.org/stable/modules/cross_validation.html", "scikit-learn Docs", DOC, 30, I, [MV], "Every splitter and when to use it."),
    ("ROC and AUC, Clearly Explained!", Y("4jRBRDbJemM"), "StatQuest", VIDEO, 16, I, [MV], "How to compare classifiers honestly."),
    ("Kaggle Learn: Feature Engineering", "https://www.kaggle.com/learn/feature-engineering", "Kaggle", PRACTICE, 300, I, [FE], "Mutual information, encodings and clustering features, with exercises."),
    ("scikit-learn: Preprocessing data", "https://scikit-learn.org/stable/modules/preprocessing.html", "scikit-learn Docs", DOC, 40, I, [FE], "Scaling and encoding done the leak-free way."),
    ("scikit-learn: Feature selection", "https://scikit-learn.org/stable/modules/feature_selection.html", "scikit-learn Docs", DOC, 30, A, [FE], "Filter, wrapper and model-based selection."),
    ("Principal Component Analysis (PCA), Step-by-Step", Y("FgakZw6K1QQ"), "StatQuest", VIDEO, 22, I, [FE], "Dimensionality reduction without the matrix fog."),
    ("scikit-learn: Tuning the hyper-parameters of an estimator", "https://scikit-learn.org/stable/modules/grid_search.html", "scikit-learn Docs", DOC, 30, I, [HPO], "Grid, random and halving search."),
    ("Kaggle Learn: Intermediate Machine Learning", "https://www.kaggle.com/learn/intermediate-machine-learning", "Kaggle", PRACTICE, 240, I, [HPO, FE, MV], "Pipelines, cross-validation and XGBoost tuning."),
    ("Regularization Part 1: Ridge (L2) Regression", Y("Q81RR3yKn30"), "StatQuest", VIDEO, 20, I, [HPO], "Why the regularization strength is worth tuning."),
    ("XGBoost Part 1: Regression", Y("OtD8wVaFm6E"), "StatQuest", VIDEO, 26, A, [HPO, QML], "What each XGBoost parameter actually controls."),
    ("Python API Development - Comprehensive Course for Beginners", Y("0sOvCWFmrtA"), "freeCodeCamp", VIDEO, 1140, I, [DEPLOY, REST], "FastAPI, databases, tests and deployment in one project."),
    ("FastAPI Tutorial - User Guide", "https://fastapi.tiangolo.com/tutorial/", "FastAPI Docs", DOC, 180, I, [DEPLOY, REST], "Official step-by-step guide."),
    ("Made With ML", "https://madewithml.com/", "Made With ML", COURSE, 600, A, [DEPLOY, MLOPS], "End-to-end production ML with code."),
    ("Docker Tutorial for Beginners", Y("3c-iBn73dDE"), "TechWorld with Nana", VIDEO, 166, B, [DOCKER, DEPCI], "Images, containers, compose and volumes with demos."),
    ("Docker in 100 Seconds", Y("Gjnup-PuquQ"), "Fireship", VIDEO, 2, B, [DOCKER], "The idea in two minutes before the long course."),
    ("Docker: Get started", "https://docs.docker.com/get-started/", "Docker Docs", DOC, 90, B, [DOCKER, DEPCI], "Official guide to build and run your first image."),
    ("Play with Docker", "https://labs.play-with-docker.com/", "Docker", PRACTICE, 60, B, [DOCKER], "A free Docker terminal in the browser."),
    ("MLOps Zoomcamp", "https://github.com/DataTalksClub/mlops-zoomcamp", "DataTalks.Club", GITHUB, 1200, A, [MLOPS], "Free course on tracking, pipelines, deployment and monitoring."),
    ("MLflow documentation", "https://mlflow.org/docs/latest/index.html", "MLflow Docs", DOC, 60, A, [MLOPS], "Experiment tracking and model registry reference."),
    ("Rules of Machine Learning", "https://developers.google.com/machine-learning/guides/rules-of-ml", "Google", ARTICLE, 45, A, [MLOPS], "Hard-won production lessons from Google."),
    ("MLOps Course - Build Machine Learning Production Grade Projects", Y("-dJPoLm_gtE"), "freeCodeCamp", VIDEO, 250, A, [MLOPS], "A full MLOps project on video."),
    # ---------------- Backend ----------------
    ("RESTful APIs in 100 Seconds", Y("-MTSQjw5DrM"), "Fireship", VIDEO, 11, B, [REST, MAPI, APISEC], "REST vocabulary in a few minutes."),
    ("HTTP response status codes", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status", "MDN", DOC, 20, B, [REST, APISEC], "Pick the right status code every time."),
    ("Web API design best practices", "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design", "Microsoft Learn", ARTICLE, 40, I, [REST], "Resource naming, versioning and pagination rules."),
    ("JSONPlaceholder: free fake REST API", "https://jsonplaceholder.typicode.com/", "JSONPlaceholder", PRACTICE, 30, B, [REST, MAPI, APISEC], "An API to practise calls against."),
    ("Database Indexing Explained", Y("-qNSXK7s7_w"), "Hussein Nasser", VIDEO, 18, I, [DBIDX], "Shows a query before and after an index."),
    ("Use The Index, Luke", "https://use-the-index-luke.com/", "Markus Winand", TUTORIAL, 240, I, [DBIDX], "The standard free guide to SQL indexing."),
    ("SQLAlchemy ORM Quick Start", "https://docs.sqlalchemy.org/en/20/orm/quickstart.html", "SQLAlchemy Docs", DOC, 40, I, [DBIDX], "Models, sessions and queries in the 2.0 style."),
    ("PostgreSQL: Using EXPLAIN", "https://www.postgresql.org/docs/current/using-explain.html", "PostgreSQL Docs", DOC, 30, A, [DBIDX], "Read query plans to find slow queries."),
    ("What Is JWT and Why Should You Use JWT", Y("7Q17ubqLfaM"), "Web Dev Simplified", VIDEO, 15, B, [AUTH, APISEC], "Token structure and verification, clearly."),
    ("Session vs Token Authentication in 100 Seconds", Y("UBUNrFtufWo"), "Fireship", VIDEO, 2, B, [AUTH], "The trade-off behind every login system."),
    ("OAuth 2.0 and OpenID Connect (in plain English)", Y("996OiexHze0"), "OktaDev", VIDEO, 62, I, [AUTH, CRYPTO], "The clearest walkthrough of the OAuth flows."),
    ("Introduction to JSON Web Tokens", "https://www.jwt.io/introduction", "jwt.io", DOC, 15, B, [AUTH], "Reference for header, payload and signature."),
    ("OWASP Authentication Cheat Sheet", "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html", "OWASP", DOC, 30, I, [AUTH, CRYPTO, APISEC], "The checklist security reviewers use."),
    ("Python Asynchronous Programming - AsyncIO & Async/Await", Y("t5Bo1Je9EmE"), "Tech With Tim", VIDEO, 25, I, [ASYNC], "Event loop, tasks and await with small examples."),
    ("asyncio - Asynchronous I/O", "https://docs.python.org/3/library/asyncio.html", "Python Docs", DOC, 60, A, [ASYNC], "Official reference for tasks, queues and locks."),
    ("Async IO in Python: A Complete Walkthrough", "https://realpython.com/async-io-python/", "Real Python", ARTICLE, 60, I, [ASYNC], "Long-form guide with runnable code."),
    ("FastAPI: Concurrency and async / await", "https://fastapi.tiangolo.com/async/", "FastAPI Docs", DOC, 20, I, [ASYNC], "When to use async def in an API."),
    # ---------------- Frontend ----------------
    ("Learn JavaScript - Full Course for Beginners", Y("PkZNo7MFNFg"), "freeCodeCamp", VIDEO, 207, B, [JS], "All language basics in one video."),
    ("The Modern JavaScript Tutorial", "https://javascript.info/", "javascript.info", TUTORIAL, 600, B, [JS], "The most complete free JavaScript text, with tasks."),
    ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "MDN", DOC, 180, B, [JS], "The reference every web developer keeps open."),
    ("Exercism JavaScript track", "https://exercism.org/tracks/javascript", "Exercism", PRACTICE, 90, B, [JS], "Graded exercises with feedback."),
    ("React Course - Beginner's Tutorial for React JavaScript Library", Y("bMknfKXIFA8"), "freeCodeCamp", VIDEO, 710, B, [REACT], "Builds several projects with modern React."),
    ("React in 100 Seconds", Y("Tn6-PIqc4UM"), "Fireship", VIDEO, 2, B, [REACT], "The mental model before the long course."),
    ("React: Quick Start", "https://react.dev/learn", "React Docs", DOC, 60, B, [REACT], "Official introduction to components, props and state."),
    ("Tutorial: Tic-Tac-Toe", "https://react.dev/learn/tutorial-tic-tac-toe", "React Docs", PRACTICE, 90, B, [REACT], "Build a small game in the browser."),
    ("Thinking in React", "https://react.dev/learn/thinking-in-react", "React Docs", DOC, 25, I, [REACT, RQ], "How to split a UI into components and state."),
    ("Learn TypeScript - Full Tutorial", Y("30LWjhZzg50"), "freeCodeCamp", VIDEO, 285, B, [TS], "From first type annotation to generics."),
    ("TypeScript in 100 Seconds", Y("zQnBQ4tB3ZA"), "Fireship", VIDEO, 2, B, [TS], "Why types catch bugs before runtime."),
    ("The TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html", "TypeScript Docs", DOC, 240, I, [TS], "The official language guide."),
    ("Type Challenges", "https://github.com/type-challenges/type-challenges", "type-challenges", PRACTICE, 300, A, [TS], "Type-level puzzles from easy to extreme."),
    ("React TypeScript Cheatsheets", "https://react-typescript-cheatsheet.netlify.app/", "Community", DOC, 60, I, [TS], "Typing props, hooks and events in React."),
    ("React Query in 100 Seconds", Y("novnyCaa7To"), "Fireship", VIDEO, 2, B, [RQ], "Server state versus client state in two minutes."),
    ("TanStack Query: Overview", "https://tanstack.com/query/latest/docs/framework/react/overview", "TanStack Docs", DOC, 45, I, [RQ], "Official guide to queries, mutations and caching."),
    ("React: Managing State", "https://react.dev/learn/managing-state", "React Docs", DOC, 120, I, [RQ, MSTATE], "Lifting state, reducers and context."),
    ("Practical React Query", "https://tkdodo.eu/blog/practical-react-query", "TkDodo", ARTICLE, 20, I, [RQ], "Advice from a TanStack Query maintainer."),
    ("Redux Essentials", "https://redux.js.org/tutorials/essentials/part-1-overview-concepts", "Redux Docs", TUTORIAL, 180, I, [RQ, MSTATE], "Store, actions and reducers with Redux Toolkit."),
    ("Learn useMemo In 10 Minutes", Y("THL1OPn72vo"), "Web Dev Simplified", VIDEO, 10, I, [PERF], "When memoizing a value helps and when it does not."),
    ("Learn useCallback In 8 Minutes", Y("_AyFP5s69N4"), "Web Dev Simplified", VIDEO, 8, I, [PERF], "Stable function references for memoized children."),
    ("React: memo", "https://react.dev/reference/react/memo", "React Docs", DOC, 20, I, [PERF], "Official rules for skipping re-renders."),
    ("Web Vitals", "https://web.dev/articles/vitals", "web.dev", ARTICLE, 20, I, [PERF], "The metrics that define a fast page."),
    ("You Might Not Need an Effect", "https://react.dev/learn/you-might-not-need-an-effect", "React Docs", DOC, 30, A, [PERF, REACT], "Removes the most common cause of wasted renders."),
    # ---------------- Data engineering ----------------
    ("Dimensional Modeling Techniques", "https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/", "Kimball Group", ARTICLE, 90, I, [DM], "Star schemas from the people who defined them."),
    ("What is dbt?", "https://docs.getdbt.com/docs/introduction", "dbt Docs", DOC, 30, I, [DM], "How modern warehouses are modelled in SQL."),
    ("7 Database Paradigms", Y("W2Z7fbCLSTw"), "Fireship", VIDEO, 10, B, [DM], "Which kind of database fits which workload."),
    ("Data Engineering Zoomcamp", "https://github.com/DataTalksClub/data-engineering-zoomcamp", "DataTalks.Club", GITHUB, 1500, I, [DM, SPARK, AIRFLOW], "Free project-based data engineering course."),
    ("PySpark Tutorial", Y("_C8kWso4ne4"), "freeCodeCamp", VIDEO, 110, I, [SPARK], "DataFrames, missing values and MLlib on video."),
    ("PySpark: Getting Started", "https://spark.apache.org/docs/latest/api/python/getting_started/index.html", "Apache Spark Docs", DOC, 60, I, [SPARK], "Official quickstart notebooks."),
    ("Spark SQL, DataFrames and Datasets Guide", "https://spark.apache.org/docs/latest/sql-programming-guide.html", "Apache Spark Docs", DOC, 90, A, [SPARK], "Reference for the API you will use daily."),
    ("Airflow Tutorial for Beginners - Full Course in 2 Hours", Y("K9AnJ9_ZAXE"), "coder2j", VIDEO, 120, B, [AIRFLOW], "Install Airflow and write DAGs from scratch."),
    ("Airflow Tutorials", "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html", "Apache Airflow Docs", DOC, 90, I, [AIRFLOW], "Official DAG tutorials."),
    ("Airflow Best Practices", "https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html", "Apache Airflow Docs", DOC, 30, A, [AIRFLOW], "Idempotent tasks and other production rules."),
    # ---------------- DevOps ----------------
    ("Linux Operating System - Crash Course for Beginners", Y("ROjZy1WbCIA"), "freeCodeCamp", VIDEO, 150, B, [LINUX], "Filesystem, permissions and processes."),
    ("Bash Scripting Tutorial for Beginners", Y("tK9Oc6AEnR4"), "freeCodeCamp", VIDEO, 48, B, [LINUX], "Variables, loops and scripts you can reuse."),
    ("OverTheWire: Bandit", "https://overthewire.org/wargames/bandit/", "OverTheWire", PRACTICE, 300, B, [LINUX, PENTEST], "Learn the shell by solving 30+ levels."),
    ("The Linux Command Line (free book)", "https://linuxcommand.org/tlcl.php", "William Shotts", ARTICLE, 600, B, [LINUX], "The standard free book on the shell."),
    ("The Missing Semester of Your CS Education", "https://missing.csail.mit.edu/", "MIT", COURSE, 600, B, [LINUX], "Shell, editors, git and debugging lectures."),
    ("Kubernetes Tutorial for Beginners", Y("X48VuDVv0do"), "TechWorld with Nana", VIDEO, 216, B, [K8S], "Pods to Ingress with a full demo project."),
    ("Kubernetes Explained in 100 Seconds", Y("PziYflu8cB8"), "Fireship", VIDEO, 2, B, [K8S], "What Kubernetes is for, in two minutes."),
    ("Kubernetes Basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "Kubernetes Docs", TUTORIAL, 120, B, [K8S], "Official interactive walkthrough."),
    ("Killercoda Kubernetes playground", "https://killercoda.com/playgrounds/scenario/kubernetes", "Killercoda", PRACTICE, 60, I, [K8S], "A free cluster in the browser."),
    ("Terraform Course - Automate your AWS cloud infrastructure", Y("SLB_c_ayRMo"), "freeCodeCamp", VIDEO, 140, B, [TF], "Providers, state and modules on a real AWS setup."),
    ("Terraform in 100 Seconds", Y("tomUWcQ0P3k"), "Fireship", VIDEO, 2, B, [TF], "Infrastructure as code in two minutes."),
    ("Terraform tutorials", "https://developer.hashicorp.com/terraform/tutorials", "HashiCorp", TUTORIAL, 300, B, [TF], "Official hands-on tracks."),
    ("Terraform language documentation", "https://developer.hashicorp.com/terraform/language", "HashiCorp", DOC, 120, I, [TF], "Reference for resources, variables and modules."),
    ("GitHub Actions Tutorial - Basic Concepts and CI/CD Pipeline with Docker", Y("R8_veQiYBjI"), "TechWorld with Nana", VIDEO, 32, B, [CICD, DEPCI], "A working pipeline in half an hour."),
    ("DevOps CI/CD Explained in 100 Seconds", Y("scEDHsr3APg"), "Fireship", VIDEO, 2, B, [CICD, DEPCI], "Why pipelines exist."),
    ("GitHub Actions documentation", "https://docs.github.com/en/actions", "GitHub Docs", DOC, 90, I, [CICD, DEPCI], "Workflow syntax and examples."),
    ("Continuous Integration", "https://martinfowler.com/articles/continuousIntegration.html", "Martin Fowler", ARTICLE, 40, I, [CICD, DEPCI], "The practices behind the tooling."),
    ("DevOps Engineering Course for Beginners", Y("j5Zsa_eOXeY"), "freeCodeCamp", VIDEO, 150, B, [CICD, DEPCI], "Testing, CI, deployment and monitoring overview."),
    # ---------------- Security ----------------
    ("Computer Networking Course - Network Engineering", Y("qiQR5rTSshw"), "freeCodeCamp", VIDEO, 565, B, [NET], "OSI model, IP, routing and protocols."),
    ("Cloudflare Learning Center", "https://www.cloudflare.com/learning/", "Cloudflare", ARTICLE, 180, B, [NET], "Short articles on DNS, TLS, DDoS and more."),
    ("How DNS works", "https://dnsimple.com/comics/how-dns-works/", "DNSimple", TUTORIAL, 15, B, [NET], "A comic that makes DNS resolution stick."),
    ("TLS Handshake Explained", Y("86cQJ0MMses"), "Computerphile", VIDEO, 17, I, [NET, CRYPTO], "What happens before the padlock appears."),
    ("TryHackMe: Pre Security path", "https://tryhackme.com/path/outline/presecurity", "TryHackMe", PRACTICE, 600, B, [NET], "Guided networking and Linux labs."),
    ("OWASP Top Ten", "https://owasp.org/projects/top-ten", "OWASP", DOC, 60, B, [WEBSEC, APISEC], "The reference list of web risks."),
    ("PortSwigger Web Security Academy", "https://portswigger.net/web-security", "PortSwigger", PRACTICE, 1200, I, [WEBSEC, PENTEST, APISEC], "Free labs for every major vulnerability class."),
    ("Running an SQL Injection Attack", Y("ciNHn38EyRc"), "Computerphile", VIDEO, 17, B, [WEBSEC], "Watch the attack so the defence makes sense."),
    ("Cracking Websites with Cross Site Scripting", Y("L5l9lSnNMxg"), "Computerphile", VIDEO, 9, B, [WEBSEC], "XSS demonstrated on a real page."),
    ("OWASP Juice Shop", "https://owasp.org/projects/juice-shop", "OWASP", PRACTICE, 600, I, [WEBSEC, PENTEST], "A deliberately vulnerable shop to attack legally."),
    ("OWASP API Security Top 10", "https://owasp.org/projects/api-security-project", "OWASP", DOC, 45, I, [APISEC], "The risks specific to APIs."),
    ("Cross-Origin Resource Sharing (CORS)", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS", "MDN", DOC, 30, I, [APISEC], "Why the browser blocks your API call."),
    ("Using the Fetch API", "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch", "MDN", DOC, 30, B, [APISEC], "Calling APIs from the browser."),
    ("Public Key Cryptography", Y("GSIDS_lvRv4"), "Computerphile", VIDEO, 6, B, [CRYPTO], "Key pairs explained with colours."),
    ("SHA: Secure Hashing Algorithm", Y("DMtFhACPnTY"), "Computerphile", VIDEO, 10, I, [CRYPTO], "What a hash function does inside."),
    ("The Cryptopals Crypto Challenges", "https://cryptopals.com/", "Cryptopals", PRACTICE, 900, A, [CRYPTO], "Break real crypto mistakes in code."),
    ("Practical Cryptography for Developers", "https://cryptobook.nakov.com/", "Svetlin Nakov", ARTICLE, 300, I, [CRYPTO], "Free book with code examples."),
    ("OWASP Password Storage Cheat Sheet", "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html", "OWASP", DOC, 20, I, [CRYPTO, AUTH], "Current guidance on hashing passwords."),
    ("Ethical Hacking in 12 Hours - Full Course", Y("fNzpcB7ODxQ"), "The Cyber Mentor", VIDEO, 720, B, [PENTEST], "Recon, exploitation and reporting, end to end."),
    ("OWASP Web Security Testing Guide", "https://owasp.org/projects/web-security-testing-guide", "OWASP", DOC, 300, A, [PENTEST], "The methodology used in real audits."),
    ("Hack The Box Academy", "https://academy.hackthebox.com/", "Hack The Box", PRACTICE, 900, I, [PENTEST], "Guided modules with live targets."),
    ("Nmap Reference Guide", "https://nmap.org/book/man.html", "Nmap", DOC, 60, I, [PENTEST, NET], "Scanning options explained by the authors."),
    # ---------------- Mobile ----------------
    ("Flutter Course for Beginners", Y("VPvVD8t02U8"), "freeCodeCamp", VIDEO, 2220, B, [MUI, MSTATE], "A complete app from setup to release."),
    ("Flutter in 100 Seconds", Y("lHhRhPV--G0"), "Fireship", VIDEO, 2, B, [MUI], "The widget model in two minutes."),
    ("React Native in 100 Seconds", Y("gvkqT_Uoahw"), "Fireship", VIDEO, 2, B, [MUI, MSTATE], "How React maps to native views."),
    ("Android Basics with Compose", "https://developer.android.com/courses/android-basics-compose/course", "Google", COURSE, 1800, B, [MUI, MNATIVE], "Google's official beginner course."),
    ("React Native: Getting started", "https://reactnative.dev/docs/getting-started", "React Native Docs", DOC, 60, B, [MUI], "Official introduction and core components."),
    ("Flutter learning pathway", "https://docs.flutter.dev/learn/pathway", "Flutter Docs", PRACTICE, 180, B, [MUI], "Guided codelabs from first app onward."),
    ("Flutter: State management introduction", "https://docs.flutter.dev/data-and-backend/state-mgmt/intro", "Flutter Docs", DOC, 60, I, [MSTATE], "Ephemeral versus app state and the common options."),
    ("State and Jetpack Compose", "https://developer.android.com/develop/ui/compose/state", "Android Docs", DOC, 45, I, [MSTATE], "State hoisting and recomposition."),
    ("GraphQL Explained in 100 Seconds", Y("eIQh02xuVw4"), "Fireship", VIDEO, 2, B, [MAPI], "Queries, mutations and the schema."),
    ("Introduction to GraphQL", "https://graphql.org/learn/", "GraphQL Docs", DOC, 90, I, [MAPI], "Official guide to the query language."),
    ("React Native: Networking", "https://reactnative.dev/docs/network", "React Native Docs", DOC, 20, B, [MAPI], "Fetch and WebSockets in an app."),
    ("Flutter: Fetch data from the internet", "https://docs.flutter.dev/cookbook/networking/fetch-data", "Flutter Docs", DOC, 30, B, [MAPI], "HTTP calls and JSON parsing recipe."),
    ("Android Development for Beginners - Full Course", Y("fis26HvvDII"), "freeCodeCamp", VIDEO, 690, B, [MNATIVE, MUI], "Activities, permissions and device features."),
    ("OWASP Mobile Top 10", "https://owasp.org/projects/mobile-top-10", "OWASP", DOC, 45, I, [MNATIVE], "The main mobile security risks."),
    ("Android: Request runtime permissions", "https://developer.android.com/training/permissions/requesting", "Android Docs", DOC, 30, I, [MNATIVE], "The correct permission flow."),
    ("OWASP Mobile Application Security Testing Guide", "https://mas.owasp.org/MASTG/", "OWASP", DOC, 300, A, [MNATIVE], "How mobile apps are audited."),
    ("Expo SDK reference", "https://docs.expo.dev/versions/latest/", "Expo Docs", DOC, 60, I, [MNATIVE], "Camera, location, secure storage and other device APIs."),
    # ---------------- General software ----------------
    ("10 Design Patterns Explained in 10 Minutes", Y("tv-_1er1mWI"), "Fireship", VIDEO, 11, B, [ARCH], "The patterns you will meet first."),
    ("Refactoring Guru: Design Patterns", "https://refactoring.guru/design-patterns", "Refactoring Guru", TUTORIAL, 300, I, [ARCH], "Every pattern with diagrams and code."),
    ("The Twelve-Factor App", "https://12factor.net/", "12factor", ARTICLE, 45, I, [ARCH, DEPCI], "Rules for apps that deploy cleanly."),
    ("The System Design Primer", "https://github.com/donnemartin/system-design-primer", "Donne Martin", GITHUB, 600, A, [ARCH], "Scalability topics with worked examples."),
    ("Software Architecture Guide", "https://martinfowler.com/architecture/", "Martin Fowler", ARTICLE, 60, I, [ARCH], "What architecture is and why it matters."),
    ("Git and GitHub for Beginners - Crash Course", Y("RGOj5yH7evk"), "freeCodeCamp", VIDEO, 68, B, [DEPCI, QPY], "Commit and push your work from day one."),
    ("Designing Data-Intensive Applications (book)", BK("Designing Data-Intensive Applications Kleppmann"), "Martin Kleppmann", BOOK, 1500, A, [ARCH, DM], "Storage engines, Replication, Partitioning, Stream processing"),
    # ---------------- Quant finance ----------------
    ("Algorithmic Trading Using Python - Full Course", Y("xfzGZB4HhEE"), "freeCodeCamp", VIDEO, 260, I, [QPY, QMOM, QBT], "Builds index, momentum and value strategies in code."),
    ("Python Programming for Finance playlist", PL("PLQVvvaa0QuDcOdF96TBtRtuQksErCEBYZ"), "sentdex", VIDEO, 400, B, [QPY], "Price data, charts and simple strategies with pandas."),
    ("yfinance: download market data", "https://github.com/ranaroussi/yfinance", "yfinance", GITHUB, 20, B, [QPY], "The free data source used throughout this track."),
    ("NumPy: the absolute basics for beginners", "https://numpy.org/doc/stable/user/absolute_beginners.html", "NumPy Docs", DOC, 45, B, [QPY], "Arrays and vectorized maths."),
    ("Python for Finance (book)", BK("Python for Finance Hilpisch"), "Yves Hilpisch", BOOK, 1500, I, [QPY], "pandas for finance, Data visualization, Stochastics, Derivatives analytics"),
    ("Essence of linear algebra", PL("PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"), "3Blue1Brown", VIDEO, 240, B, [QSTAT, QRISK], "Vectors, matrices and eigenvalues, visually."),
    ("Zerodha Varsity: Introduction to Stock Markets", "https://zerodha.com/varsity/module/introduction-to-stock-markets/", "Zerodha Varsity", COURSE, 300, B, [QMKT], "How Indian markets, orders and settlement work."),
    ("Financial Markets (Yale, Robert Shiller)", PL("PL8FB14A2200B87185"), "Yale", VIDEO, 1500, B, [QMKT], "A Nobel laureate's survey of instruments and institutions."),
    ("Khan Academy: Finance and capital markets", "https://www.khanacademy.org/economics-finance-domain/core-finance", "Khan Academy", COURSE, 600, B, [QMKT, QOPT], "Stocks, bonds, futures and options from first principles."),
    ("Finance Theory I (MIT 15.401)", PL("PLUl4u3cNGP63B2lDhyKOsImI7FjCf6eDW"), "MIT OpenCourseWare", VIDEO, 1500, I, [QMKT, QOPT, QRISK], "Present value, CAPM, futures and options with Andrew Lo."),
    ("Limit Order", "https://www.investopedia.com/terms/l/limitorder.asp", "Investopedia", ARTICLE, 10, B, [QMKT], "Limit versus market orders in plain words."),
    ("Quantopian Lecture Series (notebooks)", "https://github.com/quantopian/research_public", "Quantopian", GITHUB, 900, I, [QBT, QMR, QALPHA, QRISK], "Notebooks on statistics, pairs trading, factors and risk."),
    ("QuantConnect Learning Center", "https://www.quantconnect.com/learning/", "QuantConnect", COURSE, 600, I, [QBT, QLIVE], "Free interactive courses that end in a running strategy."),
    ("vectorbt documentation", "https://vectorbt.dev/", "vectorbt", DOC, 60, I, [QBT, QMOM], "Fast vectorized backtesting in pandas."),
    ("Backtrader Quickstart", "https://www.backtrader.com/docu/quickstart/quickstart/", "Backtrader", DOC, 60, I, [QBT], "An event-driven backtest, step by step."),
    ("Sharpe Ratio", "https://www.investopedia.com/terms/s/sharperatio.asp", "Investopedia", ARTICLE, 10, B, [QBT], "Definition, formula and pitfalls."),
    ("Quantitative Trading (book)", BK("Quantitative Trading Ernest Chan"), "Ernest Chan", BOOK, 900, I, [QBT, QMR], "Backtesting, Transaction costs, Money and risk management, Mean reversion"),
    ("Time Series Analysis playlist", PL("PLvcbYUQ5t0UHOLnBzl46_Q6QKtFgfMGc3"), "ritvikmath", VIDEO, 600, I, [QTS], "ACF, PACF, ARIMA and stationarity in short videos."),
    ("statsmodels: Time Series analysis", "https://www.statsmodels.org/stable/tsa.html", "statsmodels Docs", DOC, 60, I, [QTS, QMR], "ADF, ARIMA and cointegration functions."),
    ("Forecasting: Principles and Practice (free book)", "https://otexts.com/fpp3/", "Hyndman & Athanasopoulos", ARTICLE, 900, I, [QTS], "The standard free text on time series."),
    ("Kaggle Learn: Time Series", "https://www.kaggle.com/learn/time-series", "Kaggle", PRACTICE, 300, I, [QTS, QML], "Trend, seasonality and lag features with exercises."),
    ("Topics in Mathematics with Applications in Finance (MIT 18.S096)", PL("PLUl4u3cNGP63ctJIEC1UnZ0btsphnnoHR"), "MIT OpenCourseWare", VIDEO, 1800, A, [QTS, QMR, QRISK, QOPT, QSTAT], "Lectures by practitioners on time series, portfolio theory, VaR and Black-Scholes."),
    ("Zerodha Varsity: Trading Systems (pair trading)", "https://zerodha.com/varsity/module/trading-systems/", "Zerodha Varsity", COURSE, 300, I, [QMR], "Pair trading worked through on Indian stocks."),
    ("statsmodels: coint (Engle-Granger test)", "https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html", "statsmodels Docs", DOC, 10, I, [QMR], "The exact function for testing a pair."),
    ("Algorithmic Trading: Winning Strategies and Their Rationale (book)", BK("Algorithmic Trading Winning Strategies Ernest Chan"), "Ernest Chan", BOOK, 900, A, [QMR, QMOM], "Mean reversion of stocks and ETFs, Cointegration, Momentum strategies, Risk management"),
    ("Zerodha Varsity: Technical Analysis", "https://zerodha.com/varsity/module/technical-analysis/", "Zerodha Varsity", COURSE, 400, B, [QMOM], "Indicators and chart reading on Indian markets."),
    ("Relative Strength Index (RSI)", "https://www.investopedia.com/terms/r/rsi.asp", "Investopedia", ARTICLE, 10, B, [QMOM], "Formula and conventional thresholds."),
    ("Moving Average Convergence Divergence (MACD)", "https://www.investopedia.com/terms/m/macd.asp", "Investopedia", ARTICLE, 10, B, [QMOM], "How the indicator is built and read."),
    ("Machine Learning for Trading (Georgia Tech CS 7646)", "https://lucylabs.gatech.edu/ml4t/", "Georgia Tech", COURSE, 2400, I, [QML, QBT], "The free university course on ML-driven strategies."),
    ("Algorithmic Trading - Machine Learning & Quant Strategies Course with Python", Y("9Y3yaoi9rUQ"), "freeCodeCamp", VIDEO, 180, A, [QML, QALPHA], "Three ML strategy projects built on video."),
    ("scikit-learn: TimeSeriesSplit", "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html", "scikit-learn Docs", DOC, 10, I, [QML], "The splitter that prevents look-ahead in validation."),
    ("Machine Learning for Algorithmic Trading (code)", "https://github.com/stefan-jansen/machine-learning-for-trading", "Stefan Jansen", GITHUB, 1200, A, [QML, QALPHA], "150+ notebooks from data to deployed strategy."),
    ("Advances in Financial Machine Learning (book)", BK("Advances in Financial Machine Learning Lopez de Prado"), "Marcos Lopez de Prado", BOOK, 1500, A, [QML, QALPHA], "Labeling, Purged cross-validation, Feature importance, Backtest overfitting"),
    ("PyPortfolioOpt documentation", "https://pyportfolioopt.readthedocs.io/en/latest/", "PyPortfolioOpt", DOC, 60, I, [QRISK], "Mean-variance optimization in a few lines."),
    ("Zerodha Varsity: Risk Management & Trading Psychology", "https://zerodha.com/varsity/module/risk-management/", "Zerodha Varsity", COURSE, 300, I, [QRISK], "Position sizing, portfolio variance and VaR."),
    ("Value at Risk (VaR)", "https://www.investopedia.com/terms/v/var.asp", "Investopedia", ARTICLE, 10, B, [QRISK], "What VaR does and does not tell you."),
    ("Alpaca API documentation", "https://docs.alpaca.markets/", "Alpaca Docs", DOC, 90, I, [QLIVE], "Free paper-trading API used for the live project."),
    ("Kite Connect API documentation", "https://kite.trade/docs/connect/v3/", "Zerodha Kite Connect", DOC, 90, I, [QLIVE], "The most used Indian broker API."),
    ("QuantConnect documentation", "https://www.quantconnect.com/docs/v2", "QuantConnect", DOC, 120, I, [QLIVE, QBT], "Cloud backtesting and paper trading platform."),
    ("Zerodha Varsity: Options Theory for Professional Trading", "https://zerodha.com/varsity/module/option-theory/", "Zerodha Varsity", COURSE, 600, I, [QOPT], "Payoffs, Greeks and volatility on NIFTY options."),
    ("Introduction to the Black-Scholes formula", Y("pr-u4LCFYEY"), "Khan Academy", VIDEO, 11, I, [QOPT], "The formula's inputs and intuition."),
    ("Options Industry Council: options education", "https://www.optionseducation.org/", "OIC", COURSE, 300, B, [QOPT], "Free courses and calculators from the industry body."),
    ("Options, Futures, and Other Derivatives (book)", BK("Options Futures and Other Derivatives Hull"), "John Hull", BOOK, 2400, A, [QOPT], "Futures and forwards, Black-Scholes-Merton, The Greeks, Volatility smiles"),
    ("101 Formulaic Alphas (paper)", "https://arxiv.org/abs/1601.00991", "arXiv", ARTICLE, 60, A, [QALPHA], "Real signal formulas published by a quant firm."),
    ("WorldQuant BRAIN", "https://platform.worldquantbrain.com/", "WorldQuant", PRACTICE, 600, A, [QALPHA], "Submit alphas and get scored on real data."),
    ("Kenneth French Data Library", "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html", "Dartmouth", DOC, 30, A, [QALPHA], "Free factor returns for your regressions."),
    ("alphalens-reloaded", "https://github.com/stefan-jansen/alphalens-reloaded", "Stefan Jansen", GITHUB, 60, A, [QALPHA], "IC and quantile analysis for a factor."),
    ("Brainstellar: quant puzzles", "https://brainstellar.com/", "Brainstellar", PRACTICE, 600, I, [QINT, QSTAT], "Interview puzzles sorted by difficulty."),
    ("Jane Street Puzzles", "https://www.janestreet.com/puzzles/", "Jane Street", PRACTICE, 300, A, [QINT], "Monthly puzzles from a top trading firm."),
    ("Zetamac Arithmetic Game", "https://arithmetic.zetamac.com/", "Zetamac", PRACTICE, 10, B, [QINT], "Mental-maths drill used before trading interviews."),
    ("Project Euler", "https://projecteuler.net/", "Project Euler", PRACTICE, 600, I, [QINT, PY], "Maths problems you solve with code."),
    ("LeetCode Top Interview 150", "https://leetcode.com/studyplan/top-interview-150/", "LeetCode", PRACTICE, 1500, I, [QINT, PY], "The coding-round problems asked most."),
    ("Heard on the Street (book)", BK("Heard on the Street Timothy Crack"), "Timothy Crack", BOOK, 900, A, [QINT], "Brain teasers, Probability, Option pricing questions, Statistics"),
    ("A Practical Guide to Quantitative Finance Interviews (book)", BK("A Practical Guide to Quantitative Finance Interviews Xinfeng Zhou"), "Xinfeng Zhou", BOOK, 900, A, [QINT], "Brain teasers, Calculus and linear algebra, Probability theory, Stochastic processes"),
    # ---------------- Additions that give every skill a hands-on resource ----------------
    ("Authentication vulnerabilities (labs)", "https://portswigger.net/web-security/authentication", "PortSwigger", PRACTICE, 240, I, [AUTH], "Break weak logins in a lab, then fix your own."),
    ("aiohttp Client Quickstart", "https://docs.aiohttp.org/en/stable/client_quickstart.html", "aiohttp Docs", TUTORIAL, 40, I, [ASYNC], "Write a real concurrent HTTP client."),
    ("Learn Performance", "https://web.dev/learn/performance", "web.dev", COURSE, 240, I, [PERF], "Free course on loading and rendering speed."),
    ("GitHub Skills", "https://skills.github.com/", "GitHub", PRACTICE, 180, B, [CICD, DEPCI], "Interactive courses that run inside your own repository."),
    ("Algorithmic Stock Trading with Python - The Ultimate Beginner's Tutorial", Y("fVl1ld58xxo"), "straight-code", VIDEO, 60, B, [QLIVE], "Places paper orders through a broker API from Python."),
    ("Alpaca: Paper Trading", "https://docs.alpaca.markets/docs/paper-trading", "Alpaca Docs", PRACTICE, 60, I, [QLIVE], "A free simulated account for your first live bot."),
    ("Mathematical Trading Strategies (statistical arbitrage talk)", Y("mC_4Xiy9gnk"), "Microsoft Research", VIDEO, 80, A, [QMR], "A research talk on why pairs trading works and when it fails."),
    ("OpenQuant: quant interview questions", "https://openquant.co/questions", "OpenQuant", PRACTICE, 600, I, [QINT], "Hundreds of questions tagged by firm and topic."),
    ("TraderMath: mental maths tests", "https://www.tradermath.org/", "TraderMath", PRACTICE, 20, I, [QINT], "Timed arithmetic tests in the format trading firms use."),
]


def all_skill_names() -> List[str]:
    names: List[str] = []
    for graph in GOAL_SKILL_GRAPHS.values():
        for name, _, _ in graph:
            if name not in names:
                names.append(name)
    return names


def _skill_meta() -> Dict[str, Tuple[str, str]]:
    meta: Dict[str, Tuple[str, str]] = {}
    for graph in GOAL_SKILL_GRAPHS.values():
        for name, domain, difficulty in graph:
            meta.setdefault(name, (domain, difficulty))
    return meta


def sync_resource_library(db: Session) -> int:
    """Upserts the curated library by URL and tags each resource with its skills. Returns rows added."""
    meta = _skill_meta()
    existing = {r.url: r for r in db.query(Resource).all()}
    skill_cache: Dict[str, Skill] = {}
    added = 0
    for title, url, provider, rtype, minutes, difficulty, skills, why in RESOURCE_LIBRARY:
        resource = existing.get(url)
        if resource is None:
            resource = Resource(
                title=title, url=url, provider=provider, resource_type=rtype, description=why,
                duration_minutes=minutes, difficulty=difficulty,
                quality_score=0.92, relevance_score=0.94, freshness_score=0.90, engagement_score=0.88,
                verified=True,
            )
            db.add(resource)
            db.flush()
            existing[url] = resource
            added += 1
        tagged = {rs.skill_id for rs in db.query(ResourceSkill).filter(ResourceSkill.resource_id == resource.id).all()}
        for skill_name in skills:
            if skill_name not in skill_cache:
                domain, diff = meta.get(skill_name, ("General", "INTERMEDIATE"))
                skill_cache[skill_name] = get_or_create_skill(db, skill_name, domain, diff)
            skill = skill_cache[skill_name]
            if skill.id not in tagged:
                db.add(ResourceSkill(resource_id=resource.id, skill_id=skill.id))
                tagged.add(skill.id)
    db.commit()
    return added
