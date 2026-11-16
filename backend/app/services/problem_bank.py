"""
Practice problems, LeetCode-style: every skill has a small graded set plus links to
well-known outside problems.

In-app problems are graded on the server (answers never reach the client):
  M(id, difficulty, title, prompt, options [correct first], explanation)   multiple choice
  N(id, difficulty, title, prompt, answer, tolerance, explanation)         numeric answer
Outside problems are solved on their own site and marked as solved by the learner:
  X(id, difficulty, title, platform, url)
"""
import hashlib
import random
from typing import Dict, List, Optional

E, MED, H = "EASY", "MEDIUM", "HARD"
POINTS = {E: 10, MED: 20, H: 40}


def M(pid, diff, title, prompt, options, explanation):
    return {"id": pid, "type": "MCQ", "difficulty": diff, "title": title, "prompt": prompt,
            "options": options, "explanation": explanation}


def N(pid, diff, title, prompt, answer, tol, explanation):
    return {"id": pid, "type": "NUMERIC", "difficulty": diff, "title": title, "prompt": prompt,
            "answer": float(answer), "tolerance": float(tol), "explanation": explanation}


def X(pid, diff, title, platform, url):
    return {"id": pid, "type": "EXTERNAL", "difficulty": diff, "title": title, "platform": platform, "url": url,
            "prompt": f"Solve this on {platform}, then come back and mark it as solved."}


LC = "https://leetcode.com/problems/"
KG = "https://www.kaggle.com/"

PROBLEM_BANK: Dict[str, List[dict]] = {
    # =============== Quant finance ===============
    "Python for Quant Finance": [
        M("qpy-1", E, "Shift before you trade", "In a backtest, what does `df['signal'].shift(1)` do?",
          ["Moves each signal down one row, so today's position uses yesterday's signal", "Deletes the first signal", "Multiplies every signal by one", "Sorts the signals by date"],
          "Shifting by one bar means you only trade on information that existed before the bar you trade in."),
        N("qpy-2", MED, "Compounding returns", "Daily returns are +10%, -10% and +10%. What is the cumulative return in percent?", 8.9, 0.05,
          "1.10 x 0.90 x 1.10 = 1.089, so +8.9%. Returns compound; they do not add."),
        M("qpy-3", H, "Log returns", "Why are log returns convenient when working across many periods?",
          ["They add across time, so a multi-period return is a simple sum", "They are always larger than simple returns", "They remove volatility", "They cannot be negative"],
          "log(P_T / P_0) is the sum of the one-period log returns, which makes aggregation and statistics easier."),
        X("qpy-x1", E, "Pandas exercises", "Kaggle Learn", KG + "learn/pandas"),
        X("qpy-x2", E, "Best Time to Buy and Sell Stock", "LeetCode", LC + "best-time-to-buy-and-sell-stock/"),
    ],
    "Probability & Statistics for Trading": [
        N("qst-1", E, "Expected value of a die", "What is the expected value of one roll of a fair six-sided die?", 3.5, 0.001,
          "(1+2+3+4+5+6)/6 = 3.5."),
        N("qst-2", MED, "At least one six", "A fair die is rolled 4 times. What is the probability of at least one six? Answer as a decimal.", 0.5177, 0.005,
          "1 - (5/6)^4 = 0.5177. Use the complement."),
        N("qst-3", H, "Two heads in a row", "What is the expected number of fair coin flips needed to see two heads in a row?", 6, 0.001,
          "Let E be the answer. E = 0.5(1 + E) + 0.25(2 + E) + 0.25(2), which gives E = 6."),
        X("qst-x1", MED, "Probability puzzles", "Brainstellar", "https://brainstellar.com/"),
        X("qst-x2", MED, "Random Pick with Weight", "LeetCode", LC + "random-pick-with-weight/"),
    ],
    "Financial Markets & Instruments": [
        N("qmk-1", E, "Paying the spread", "Bid is 99.95 and ask is 100.05. You buy 100 shares at the ask and sell them at once at the bid. How many rupees do you lose (ignore fees)?", 10, 0.01,
          "You lose the spread of 0.10 on each of 100 shares = 10."),
        N("qmk-2", MED, "Short sale profit", "You short 10 shares at 500 and buy them back at 450. What is your profit in rupees (ignore fees)?", 500, 0.01,
          "A short gains when the price falls: (500 - 450) x 10 = 500."),
        M("qmk-3", H, "Beta hedge", "You hold Rs 10,00,000 of a stock with beta 1.5. To remove market exposure with index futures you should:",
          ["Short Rs 15,00,000 of index futures", "Short Rs 10,00,000 of index futures", "Buy Rs 15,00,000 of index futures", "Short Rs 6,66,667 of index futures"],
          "Hedge notional = beta x position = 1.5 x 10,00,000, and it must be short to offset a long stock."),
        X("qmk-x1", E, "Practise placing orders with virtual money", "Investopedia Simulator", "https://www.investopedia.com/simulator/"),
    ],
    "Backtesting & Performance Metrics": [
        N("qbt-1", E, "Sharpe ratio", "A strategy returns 15% a year with 10% volatility. The risk-free rate is 5%. What is the Sharpe ratio?", 1.0, 0.01,
          "(15 - 5) / 10 = 1.0."),
        N("qbt-2", MED, "Maximum drawdown", "An equity curve reads 100, 120, 90, 110, 80, 130. What is the maximum drawdown in percent?", 33.33, 0.2,
          "The worst peak-to-trough fall is from 120 to 80: 40/120 = 33.3%."),
        N("qbt-3", H, "Cost drag", "A strategy makes 250 round trips a year, each costing 0.1% of capital. Gross return is 30%. What is the approximate net annual return in percent?", 5, 0.5,
          "Costs are 250 x 0.1% = 25% a year, leaving about 5%. High turnover strategies live or die on costs."),
        X("qbt-x1", MED, "Best Time to Buy and Sell Stock II", "LeetCode", LC + "best-time-to-buy-and-sell-stock-ii/"),
        X("qbt-x2", MED, "Build and backtest a first algorithm", "QuantConnect Learning Center", "https://www.quantconnect.com/learning/"),
    ],
    "Time Series Analysis & Stationarity": [
        M("qts-1", E, "Which series is closer to stationary?", "Which of these is usually closest to stationary?",
          ["Daily returns of a stock", "The stock's price", "The stock's cumulative volume", "A market index level"],
          "Prices and index levels trend; returns fluctuate around a roughly constant mean."),
        N("qts-2", MED, "z-score", "A series has rolling mean 100 and rolling standard deviation 4. The current value is 110. What is its z-score?", 2.5, 0.01,
          "(110 - 100) / 4 = 2.5."),
        M("qts-3", H, "Differencing a random walk", "A price follows p(t) = p(t-1) + e(t), where e is white noise. What is its first difference?",
          ["White noise, which is stationary", "Another random walk", "A constant", "A series with a unit root"],
          "p(t) - p(t-1) = e(t). Differencing once removes the unit root."),
        X("qts-x1", MED, "Time Series course exercises", "Kaggle Learn", KG + "learn/time-series"),
        X("qts-x2", H, "Sliding Window Maximum", "LeetCode", LC + "sliding-window-maximum/"),
    ],
    "Mean Reversion & Pairs Trading": [
        N("qmr-1", E, "Compute the spread", "Stock A trades at 210, stock B at 100, and the hedge ratio is 2. What is the spread A - 2B?", 10, 0.01,
          "210 - 2 x 100 = 10."),
        N("qmr-2", MED, "Spread z-score", "A spread has mean 5 and standard deviation 2. It is now 0. What is its z-score?", -2.5, 0.01,
          "(0 - 5) / 2 = -2.5. A very negative z-score is a signal to buy the spread."),
        N("qmr-3", H, "Half-life of mean reversion", "A spread follows s(t) = 0.9 x s(t-1) + noise per day. What is its half-life in days (one decimal)?", 6.6, 0.2,
          "Half-life = ln(0.5) / ln(0.9) = 6.58 days. It tells you how long to expect to hold a trade."),
        X("qmr-x1", MED, "Pairs trading lecture notebook", "Quantopian Lectures (GitHub)", "https://github.com/quantopian/research_public"),
    ],
    "Momentum & Technical Signals": [
        N("qmo-1", E, "Simple moving average", "Closing prices over five days are 10, 12, 14, 16, 18. What is the 5-day simple moving average?", 14, 0.01,
          "(10+12+14+16+18)/5 = 14."),
        N("qmo-2", MED, "12-1 momentum", "A stock was 100 twelve months ago, 130 one month ago and is 125 now. What is its 12-1 momentum in percent (skipping the latest month)?", 30, 0.1,
          "12-1 momentum uses the return from 12 months ago to 1 month ago: 130/100 - 1 = 30%."),
        N("qmo-3", H, "Volatility targeting", "Your target volatility is 10% and the asset's volatility is 25%. What weight in percent should you hold?", 40, 0.1,
          "Weight = target vol / asset vol = 10/25 = 40%."),
        X("qmo-x1", MED, "Online Stock Span", "LeetCode", LC + "online-stock-span/"),
    ],
    "Machine Learning for Trading": [
        M("qml-1", E, "Choosing the label", "You want to predict next-day direction. What is the right label for day t?",
          ["The sign of the return from the close of day t to the close of day t+1", "The sign of the return on day t", "The closing price on day t", "The average return of the last 5 days"],
          "The label must come from the future relative to the features; everything else is a feature."),
        M("qml-2", MED, "Name the validation scheme", "You train on 2015-2019 and test on 2020, then train on 2015-2020 and test on 2021. This is:",
          ["Expanding-window walk-forward validation", "Stratified k-fold", "Leave-one-out cross-validation", "Bootstrap aggregation"],
          "Each test period comes strictly after its training data, as it would in live trading."),
        N("qml-3", H, "Break-even accuracy", "Each trade wins +1% or loses -1%, and costs 0.1% per trade. What win rate in percent is needed to break even?", 55, 0.1,
          "p(1) - (1-p)(1) - 0.1 = 0 gives p = 0.55."),
        X("qml-x1", H, "Optiver - Trading at the Close", "Kaggle competition", KG + "competitions/optiver-trading-at-the-close"),
        X("qml-x2", H, "Jane Street Real-Time Market Data Forecasting", "Kaggle competition", KG + "competitions/jane-street-real-time-market-data-forecasting"),
    ],
    "Risk Management & Portfolio Construction": [
        N("qrk-1", E, "Position size from risk", "You have Rs 1,00,000 and risk 1% per trade. Your stop is Rs 5 per share away from entry. How many shares can you buy?", 200, 0.01,
          "Risk budget is Rs 1,000; 1,000 / 5 = 200 shares."),
        N("qrk-2", MED, "Portfolio volatility", "Two assets each have 20% volatility and correlation 0.5. What is the volatility in percent of a 50/50 portfolio?", 17.32, 0.1,
          "Variance = 0.25x400 + 0.25x400 + 2x0.25x0.5x400 = 300; sqrt(300) = 17.3%."),
        N("qrk-3", H, "Kelly fraction", "A bet pays even money and you win 55% of the time. What fraction of capital in percent does the Kelly criterion suggest?", 10, 0.1,
          "For even odds, f = 2p - 1 = 0.10. Most practitioners bet a fraction of this."),
        X("qrk-x1", MED, "Portfolio optimization cookbook", "PyPortfolioOpt (GitHub)", "https://github.com/robertmartin8/PyPortfolioOpt"),
    ],
    "Live Trading & Broker APIs": [
        M("qlv-1", E, "Pick the order type", "You want to buy only at 100 or lower. Which order do you send?",
          ["A limit order at 100", "A market order", "A stop order at 100", "A market-on-close order"],
          "A limit order sets the worst price you will accept."),
        M("qlv-2", MED, "Safe retries", "A network timeout hides whether your order was accepted. What makes a retry safe?",
          ["Sending the same unique client order ID, so the broker rejects a duplicate", "Sending the order twice to be sure", "Waiting one minute and resending", "Switching to a market order"],
          "Idempotency keys let the broker recognise a repeat of the same request."),
        N("qlv-3", H, "Measure slippage", "Your backtest assumed buys at 100.00. Live buys average 100.08. What is the slippage in basis points?", 8, 0.1,
          "0.08 / 100 = 0.08% = 8 basis points. Feed this back into the backtest."),
        X("qlv-x1", MED, "Place your first paper order", "Alpaca paper trading", "https://docs.alpaca.markets/docs/paper-trading"),
    ],
    "Options Pricing & Greeks": [
        N("qop-1", E, "Call profit at expiry", "You buy a call with strike 100 for a premium of 5. The stock expires at 112. What is your profit per share?", 7, 0.01,
          "Payoff is 112 - 100 = 12, minus the 5 premium = 7."),
        N("qop-2", MED, "Put-call parity", "Stock is 100, strike is 100, interest rate is 0, and the call costs 8. What should the put with the same strike and expiry cost?", 8, 0.01,
          "C - P = S - K when rates are zero, so P = 8."),
        N("qop-3", H, "Delta hedge", "You are long 10 call contracts with a lot size of 50 and a delta of 0.4. How many shares must you short to be delta neutral?", 200, 0.01,
          "10 x 50 x 0.4 = 200 shares."),
        X("qop-x1", MED, "Options education and calculators", "Options Industry Council", "https://www.optionseducation.org/"),
    ],
    "Alpha Research & Factor Models": [
        M("qal-1", E, "A negative IC", "A signal has an information coefficient of -0.05, month after month. What does that suggest?",
          ["It predicts returns in reverse; flipping its sign gives a positive IC", "It has no predictive power", "It is overfit", "Its turnover is too high"],
          "A consistently negative IC is information. Consistency matters more than the sign."),
        N("qal-2", MED, "Fundamental law of active management", "A signal has IC 0.05 and makes 400 independent bets a year. What information ratio does the fundamental law predict?", 1.0, 0.02,
          "IR = IC x sqrt(breadth) = 0.05 x 20 = 1.0."),
        M("qal-3", H, "Sector neutralization", "Why do researchers subtract the sector average from a stock-level signal?",
          ["So returns come from picking stocks within a sector, not from a bet on sectors", "To increase turnover", "To make the signal positive", "To remove transaction costs"],
          "Neutralizing removes unintended exposures so you can see whether the signal itself works."),
        X("qal-x1", H, "Submit your first alpha", "WorldQuant BRAIN", "https://platform.worldquantbrain.com/"),
        X("qal-x2", H, "Implement three of the 101 Formulaic Alphas", "arXiv paper", "https://arxiv.org/abs/1601.00991"),
    ],
    "Quant Interview Problem Solving": [
        N("qin-1", E, "Is the game worth playing?", "You win Rs 6 on heads and lose Rs 4 on tails with a fair coin. What is the expected value per flip in rupees?", 1, 0.001,
          "0.5 x 6 - 0.5 x 4 = 1."),
        N("qin-2", MED, "The birthday problem", "How many people are needed in a room for the chance of a shared birthday to first exceed 50%?", 23, 0.001,
          "With 23 people the probability is about 50.7%."),
        N("qin-3", H, "Breaking a stick", "A stick of length 1 is broken at a uniformly random point. What is the expected length of the longer piece?", 0.75, 0.001,
          "The longer piece is uniform on [0.5, 1], so its mean is 0.75."),
        X("qin-x1", MED, "Implement Rand10() Using Rand7()", "LeetCode", LC + "implement-rand10-using-rand7/"),
        X("qin-x2", H, "This month's puzzle", "Jane Street Puzzles", "https://www.janestreet.com/puzzles/"),
    ],
    # =============== Programming & data ===============
    "Python Architecture": [
        M("py-1", E, "List comprehension", "What does `[x * 2 for x in range(3)]` produce?",
          ["[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2, 0, 1, 2]", "[1, 2, 3]"], "range(3) yields 0, 1, 2; each is doubled."),
        M("py-2", MED, "Lookup speed", "What is the average time complexity of `key in my_dict`?",
          ["O(1)", "O(n)", "O(log n)", "O(n log n)"], "Dictionaries are hash tables."),
        X("py-x1", E, "Two Sum", "LeetCode", LC + "two-sum/"),
        X("py-x2", MED, "Group Anagrams", "LeetCode", LC + "group-anagrams/"),
    ],
    "SQL & Analytical Queries": [
        M("sql-1", E, "Counting NULLs", "How do COUNT(*) and COUNT(email) differ?",
          ["COUNT(email) skips rows where email is NULL", "They are always equal", "COUNT(*) skips NULL rows", "COUNT(email) counts distinct emails"],
          "COUNT(column) ignores NULLs; COUNT(*) counts rows."),
        M("sql-2", MED, "Top earner per department", "Which approach returns the highest-paid employee in each department?",
          ["ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC), then keep row 1", "ORDER BY salary DESC LIMIT 1", "GROUP BY salary", "SELECT DISTINCT dept"],
          "A window function ranks within each department."),
        X("sql-x1", E, "Combine Two Tables", "LeetCode", LC + "combine-two-tables/"),
        X("sql-x2", H, "Department Top Three Salaries", "LeetCode", LC + "department-top-three-salaries/"),
    ],
    "Applied Statistics": [
        N("st-1", E, "Mean", "What is the mean of 2, 4, 6 and 8?", 5, 0.001, "(2+4+6+8)/4 = 5."),
        N("st-2", MED, "Standard error", "A sample of 100 values has standard deviation 20. What is the standard error of the mean?", 2, 0.01,
          "SE = s / sqrt(n) = 20 / 10 = 2."),
        X("st-x1", E, "Statistics and probability practice", "Khan Academy", "https://www.khanacademy.org/math/statistics-probability"),
    ],
    "Pandas & Data Manipulation": [
        M("pd-1", E, "Filter rows", "Which expression keeps rows where column `qty` is greater than 5?",
          ["df[df['qty'] > 5]", "df['qty' > 5]", "df.filter('qty' > 5)", "df.where('qty', 5)"], "Boolean indexing uses a mask of True/False values."),
        M("pd-2", MED, "Group and aggregate", "How do you get average `sales` per `city`?",
          ["df.groupby('city')['sales'].mean()", "df.mean('city', 'sales')", "df['sales'].groupby().mean('city')", "df.pivot('sales').mean()"],
          "groupby splits by key, then the aggregation runs per group."),
        X("pd-x1", E, "Introduction to Pandas study plan", "LeetCode", "https://leetcode.com/studyplan/introduction-to-pandas/"),
    ],
    "Machine Learning Foundations": [
        M("ml-1", E, "Problem type", "Predicting the sale price of a house is a:",
          ["Regression problem", "Classification problem", "Clustering problem", "Dimensionality reduction problem"], "The target is a continuous number."),
        M("ml-2", MED, "Diagnose the model", "Training accuracy is 99% and validation accuracy is 70%. What is happening?",
          ["Overfitting: the model memorised the training data", "Underfitting", "Data leakage into validation", "A perfect model"],
          "A large train/validation gap is the signature of overfitting. Simplify, regularize or add data."),
        X("ml-x1", E, "Titanic - Machine Learning from Disaster", "Kaggle competition", KG + "competitions/titanic"),
    ],
    "Model Validation & Split Hygiene": [
        M("mv-1", E, "The test set", "What is the test set for?",
          ["A final, one-time estimate of performance on unseen data", "Choosing hyperparameters", "Training the model", "Engineering features"],
          "Every decision made using the test set makes its estimate optimistic."),
        M("mv-2", MED, "Spot the leak", "You scale all the data with StandardScaler and then split into train and test. What is wrong?",
          ["Test-set statistics leaked into training through the scaler", "Nothing", "The scaler should be fitted on the test set", "Scaling is not allowed before a split for speed reasons"],
          "Fit preprocessing on the training data only, ideally inside a Pipeline."),
        X("mv-x1", MED, "House Prices - Advanced Regression Techniques", "Kaggle competition", KG + "competitions/house-prices-advanced-regression-techniques"),
    ],
    "Feature Engineering & Selection": [
        M("fe-1", E, "Encode a category", "A linear model needs the unordered column `city` with five values. Which encoding fits?",
          ["One-hot encoding", "Label encoding 1-5", "Leaving it as text", "Sorting alphabetically"], "Label numbers would invent an order that does not exist."),
        M("fe-2", MED, "Skewed feature", "When does a log transform usually help?",
          ["When a positive feature is strongly right-skewed, such as income", "When a feature is binary", "When a feature is already normal", "When a feature has negative values"],
          "The log compresses large values and makes relationships closer to linear."),
        X("fe-x1", MED, "Feature Engineering course exercises", "Kaggle Learn", KG + "learn/feature-engineering"),
    ],
    "Hyperparameter Optimization": [
        N("hp-1", E, "Size of a grid search", "A grid has 3 x 4 x 2 parameter values and uses 5-fold cross-validation. How many model fits is that?", 120, 0.001,
          "24 combinations x 5 folds = 120 fits."),
        M("hp-2", MED, "Tuning on the test set", "What happens if you pick hyperparameters by test-set score?",
          ["The reported test score becomes optimistically biased", "Training gets faster", "The model underfits", "Nothing changes"],
          "Use a validation set or cross-validation for tuning and keep the test set untouched."),
        X("hp-x1", MED, "Intermediate Machine Learning exercises", "Kaggle Learn", KG + "learn/intermediate-machine-learning"),
    ],
    "Model Deployment & APIs": [
        M("dp-1", E, "Bad input", "A client sends text where your /predict endpoint expects a number. What should the API return?",
          ["A 4xx validation error that names the bad field", "A 500 server error", "A prediction of zero", "A 200 with an empty body"],
          "Client mistakes are 4xx (FastAPI uses 422); the message should say what to fix."),
        M("dp-2", MED, "Loading the model", "Why load the model once at startup instead of in every request?",
          ["Loading is slow, and doing it per request adds latency and memory churn", "Models cannot be loaded twice", "It makes predictions more accurate", "Startup loading is required by HTTP"],
          "Keep the model in memory and reuse it."),
        X("dp-x1", MED, "Build the tutorial API end to end", "FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/"),
    ],
    "Docker & Containerization": [
        M("dk-1", E, "Image or container?", "What is the relationship between an image and a container?",
          ["A container is a running instance of an image", "An image is a running container", "They are the same thing", "A container builds images"],
          "Images are read-only templates; containers are processes started from them."),
        M("dk-2", MED, "Layer caching", "Why copy requirements.txt and install dependencies before copying the rest of the code?",
          ["So code changes do not invalidate the cached dependency layer", "Docker requires alphabetical order", "It makes the image smaller", "It avoids needing a base image"],
          "Layers are cached top to bottom; put what changes least first."),
        X("dk-x1", E, "Run your first containers", "Play with Docker", "https://labs.play-with-docker.com/"),
    ],
    "MLOps & Monitoring": [
        M("mo-1", E, "Data drift", "What is data drift?",
          ["The distribution of model inputs changes over time", "The model file is corrupted", "Training takes longer each run", "Labels are stored in the wrong format"],
          "When inputs move away from the training data, performance can decay silently."),
        M("mo-2", MED, "Model registry", "What is a model registry for?",
          ["Versioning models and controlling which one is in production", "Storing raw training data", "Scheduling cron jobs", "Serving static files"],
          "It records lineage and lets you promote or roll back versions."),
        X("mo-x1", H, "Course homework", "MLOps Zoomcamp (GitHub)", "https://github.com/DataTalksClub/mlops-zoomcamp"),
    ],
    "Exploratory Data Analysis": [
        M("ed-1", E, "See a distribution", "Which chart best shows the distribution of one numeric column?",
          ["Histogram", "Pie chart", "Line chart", "Stacked bar chart"], "A histogram shows shape, centre and spread."),
        N("ed-2", MED, "Robust centre", "What is the median of 1, 2, 3, 4 and 100?", 3, 0.001, "The middle value is 3; the outlier barely matters."),
        X("ed-x1", E, "Data Cleaning course exercises", "Kaggle Learn", KG + "learn/data-cleaning"),
    ],
    "Applied Statistics & Hypothesis Testing": [
        M("ht-1", E, "Type I error", "What is a Type I error?",
          ["Rejecting a true null hypothesis (a false positive)", "Failing to reject a false null", "Using the wrong test", "A sample that is too small"],
          "Its probability is the significance level alpha."),
        N("ht-2", MED, "Multiple testing", "You run 20 independent tests at alpha = 0.05 and every null hypothesis is true. How many false positives do you expect?", 1, 0.001,
          "20 x 0.05 = 1. This is why corrections such as Bonferroni exist."),
        X("ht-x1", MED, "Significance tests practice", "Khan Academy", "https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample"),
    ],
    "Data Visualization & Storytelling": [
        M("vz-1", E, "Trend over time", "Which chart best shows monthly revenue over three years?",
          ["Line chart", "Pie chart", "Scatter plot", "Treemap"], "Lines show change over an ordered time axis."),
        M("vz-2", MED, "Truncated axis", "What does starting a bar chart's y-axis at 90 instead of 0 do?",
          ["It exaggerates differences between bars", "It makes the chart more accurate", "Nothing", "It hides outliers"],
          "Bar length encodes value, so bars should start at zero."),
        X("vz-x1", E, "Data Visualization course exercises", "Kaggle Learn", KG + "learn/data-visualization"),
    ],
    # =============== Backend ===============
    "RESTful API Architecture": [
        M("rs-1", E, "Created", "Which status code should a successful POST that creates a resource return?",
          ["201 Created", "200 OK", "204 No Content", "302 Found"], "201 signals creation, usually with a Location header."),
        M("rs-2", MED, "Idempotency", "Which method must give the same result when repeated?",
          ["PUT", "POST", "CONNECT", "None of them"], "PUT replaces a resource, so repeating it changes nothing further."),
        X("rs-x1", E, "Call every endpoint from your own client", "JSONPlaceholder", "https://jsonplaceholder.typicode.com/"),
    ],
    "Database Indexing & ORM Hygiene": [
        M("ix-1", E, "Where an index helps", "Which query benefits most from an index on `email`?",
          ["SELECT * FROM users WHERE email = 'a@b.com'", "SELECT COUNT(*) FROM users", "SELECT * FROM users", "INSERT INTO users ..."],
          "Indexes speed up selective lookups; they slow down inserts slightly."),
        M("ix-2", MED, "N+1 queries", "A page loads 50 posts and then runs one query per post for its author. What is the fix?",
          ["Eager-load authors with a join or an IN query", "Add more application servers", "Cache the page forever", "Use a bigger connection pool"],
          "One query for posts plus one for all authors replaces 51 queries."),
        X("ix-x1", MED, "The 3-Minute Test", "Use The Index, Luke", "https://use-the-index-luke.com/3-minute-test"),
    ],
    "Authentication & JWT Security": [
        M("au-1", E, "What is in a JWT?", "The payload of a standard signed JWT is:",
          ["Base64-encoded and readable by anyone, but tamper-evident", "Encrypted", "Hashed", "Stored only on the server"],
          "Signing proves integrity, not secrecy. Never put secrets in the payload."),
        M("au-2", MED, "Storing passwords", "How should passwords be stored?",
          ["With a slow, salted hash such as bcrypt or Argon2", "With SHA-256", "Encrypted with a key kept in the code", "In plain text behind a firewall"],
          "Slow salted hashes make offline guessing expensive."),
        X("au-x1", MED, "Authentication labs", "PortSwigger Web Security Academy", "https://portswigger.net/web-security/authentication"),
    ],
    "Async Programming & Concurrency": [
        M("as-1", E, "What await does", "What happens at `await fetch_data()`?",
          ["The coroutine pauses and the event loop runs other tasks until the result is ready", "A new thread starts", "The whole program blocks", "The function is cancelled"],
          "await is a cooperative yield point."),
        N("as-2", MED, "Concurrent I/O", "Three network calls take 2 seconds each. Run with asyncio.gather, roughly how many seconds do they take in total?", 2, 0.3,
          "They wait at the same time, so the total is about the slowest call."),
        X("as-x1", E, "Print in Order", "LeetCode", LC + "print-in-order/"),
    ],
    # =============== Frontend ===============
    "JavaScript Fundamentals & ES6+": [
        M("js-1", E, "const and objects", "What does `const user = {name: 'A'}` prevent?",
          ["Reassigning `user`, but not changing its properties", "Changing any property", "Reading the object", "Garbage collection"],
          "const fixes the binding, not the value it points to."),
        M("js-2", MED, "Promise order", "What does `console.log(1); setTimeout(() => console.log(2)); Promise.resolve().then(() => console.log(3)); console.log(4)` print?",
          ["1 4 3 2", "1 2 3 4", "1 4 2 3", "1 3 4 2"], "Synchronous code first, then microtasks (promises), then timers."),
        X("js-x1", E, "30 Days of JavaScript", "LeetCode", "https://leetcode.com/studyplan/30-days-of-javascript/"),
    ],
    "React Component Architecture": [
        M("rc-1", E, "Props", "Inside a component, props are:",
          ["Read-only inputs from the parent", "Private mutable state", "Global variables", "DOM nodes"], "To change what is shown, the parent passes new props or the component uses state."),
        M("rc-2", MED, "Keys in lists", "Why does React need a stable `key` on list items?",
          ["To match items between renders and keep their state", "To style them", "To sort them", "To make them clickable"],
          "Index keys break when items are reordered or removed."),
        X("rc-x1", E, "Tutorial: Tic-Tac-Toe", "React Docs", "https://react.dev/learn/tutorial-tic-tac-toe"),
        X("rc-x2", MED, "Front-end challenges", "Frontend Mentor", "https://www.frontendmentor.io/challenges"),
    ],
    "TypeScript Integration": [
        M("ts-1", E, "Union type", "What does `string | number` mean?",
          ["The value may be a string or a number", "The value is both at once", "A string converted to a number", "An array of strings and numbers"], "A union lists the allowed alternatives."),
        M("ts-2", MED, "unknown vs any", "How does `unknown` differ from `any`?",
          ["unknown must be narrowed before use; any switches type checking off", "They are identical", "unknown is only for errors", "any is safer"],
          "Prefer unknown for values you have not validated yet."),
        X("ts-x1", MED, "Type Challenges", "GitHub", "https://github.com/type-challenges/type-challenges"),
    ],
    "State Management & React Query": [
        M("rq-1", E, "Server state", "Which of these is server state?",
          ["A list of orders fetched from an API", "Whether a modal is open", "The current input text", "The selected tab"],
          "Server state lives elsewhere and can go stale; UI state is local."),
        M("rq-2", MED, "staleTime", "What does a longer `staleTime` do in TanStack Query?",
          ["Cached data is treated as fresh for longer, so fewer refetches happen", "Data is deleted sooner", "Mutations run more slowly", "Queries retry more often"],
          "Fresh data is served from cache without a background refetch."),
        X("rq-x1", MED, "Cache With Time Limit", "LeetCode", LC + "cache-with-time-limit/"),
    ],
    "Performance Optimization & Memoization": [
        M("pf-1", E, "React.memo", "What does wrapping a component in React.memo do?",
          ["Skips re-rendering when its props have not changed", "Caches network requests", "Makes state global", "Delays rendering by one frame"],
          "It compares props shallowly."),
        M("pf-2", MED, "When useCallback matters", "When does useCallback actually help?",
          ["When the function is passed to a memoized child or used in a dependency array", "Always", "Only in class components", "When the function is async"],
          "Otherwise it only adds overhead."),
        X("pf-x1", MED, "Memoize", "LeetCode", LC + "memoize/"),
        X("pf-x2", MED, "Debounce", "LeetCode", LC + "debounce/"),
    ],
    # =============== Data engineering ===============
    "Data Modeling & Warehousing": [
        M("dm-1", E, "Fact tables", "What does a fact table store?",
          ["Measurable events such as sales, with keys to dimensions", "Descriptions of customers", "Database users", "Index definitions"],
          "Facts are the numbers; dimensions are the context."),
        M("dm-2", MED, "Type 2 dimension", "What does a Type 2 slowly changing dimension do when a customer moves city?",
          ["Adds a new row and keeps the old one for history", "Overwrites the city", "Deletes the customer", "Stores the city in the fact table"],
          "Type 2 preserves history with validity dates."),
        X("dm-x1", MED, "Advanced SQL exercises", "Kaggle Learn", KG + "learn/advanced-sql"),
    ],
    "Apache Spark & Distributed Computing": [
        M("sp-1", E, "Lazy evaluation", "When does Spark run a chain of transformations?",
          ["When an action such as count() or write is called", "Immediately, line by line", "Never", "Only at shutdown"],
          "Transformations build a plan; actions execute it."),
        M("sp-2", MED, "What shuffles?", "Which operation usually causes a shuffle?",
          ["groupBy on a key", "select of two columns", "filter on a column", "withColumn"],
          "Grouping and joining move rows between partitions."),
        X("sp-x1", MED, "Quickstart: DataFrame", "Apache Spark Docs", "https://spark.apache.org/docs/latest/api/python/getting_started/index.html"),
    ],
    "Orchestration & Airflow": [
        M("af-1", E, "The A in DAG", "Why must an Airflow DAG be acyclic?",
          ["A cycle would mean a task waits on itself and can never start", "Cycles are slow", "Python forbids loops", "The UI cannot draw circles"],
          "Dependencies must have a clear start and end."),
        M("af-2", MED, "catchup", "A DAG has start_date 30 days ago, a daily schedule and catchup=True. What happens when it is enabled?",
          ["Airflow schedules a run for each missed day", "Only today's run is created", "The DAG fails", "Nothing until tomorrow"],
          "Catchup backfills every interval since the start date."),
        X("af-x1", MED, "Fundamental Concepts tutorial", "Apache Airflow Docs", "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html"),
    ],
    # =============== DevOps ===============
    "Linux Systems & Shell Scripting": [
        M("lx-1", E, "Search files", "Which command searches every file under the current folder for the word error?",
          ["grep -r error .", "find error", "cat error", "ls -r error"], "grep -r searches recursively."),
        M("lx-2", MED, "Permissions", "What does chmod 644 file give?",
          ["Owner read/write; group and others read only", "Everyone read/write", "Owner execute only", "No access for others"],
          "6 = read+write, 4 = read."),
        X("lx-x1", E, "Bandit levels 0-10", "OverTheWire", "https://overthewire.org/wargames/bandit/"),
        X("lx-x2", E, "Tenth Line", "LeetCode", LC + "tenth-line/"),
    ],
    "Kubernetes Orchestration": [
        M("k8-1", E, "Deployments", "What does a Deployment do?",
          ["Keeps the desired number of pod replicas running and rolls out updates", "Stores secrets", "Routes external traffic", "Builds images"],
          "It manages ReplicaSets and rolling updates."),
        M("k8-2", MED, "Services", "Why put a Service in front of pods?",
          ["Pods come and go; a Service gives a stable name and load-balances across them", "To encrypt pod disks", "To schedule pods on nodes", "To build containers"],
          "Pod IPs are not stable."),
        X("k8-x1", MED, "Kubernetes playground", "Killercoda", "https://killercoda.com/playgrounds/scenario/kubernetes"),
    ],
    "Infrastructure as Code & Terraform": [
        M("tf-1", E, "terraform plan", "What does `terraform plan` do?",
          ["Shows the changes that would be made, without making them", "Applies changes", "Deletes all resources", "Formats the code"],
          "Always read the plan before applying."),
        M("tf-2", MED, "State", "What is the Terraform state file for?",
          ["Mapping your configuration to the real resources it created", "Storing provider source code", "Logging shell history", "Caching Docker layers"],
          "Without state Terraform cannot know what already exists."),
        X("tf-x1", E, "Get Started tutorials", "HashiCorp", "https://developer.hashicorp.com/terraform/tutorials"),
    ],
    "CI/CD Pipeline Automation": [
        M("ci-1", E, "Continuous integration", "What is the core idea of continuous integration?",
          ["Merge small changes often and verify each one with automated builds and tests", "Deploy once a quarter", "Test manually before release", "Keep long-lived branches"],
          "Small, frequent, verified merges keep the main branch healthy."),
        M("ci-2", MED, "Secrets", "Where should a deployment token used by a pipeline live?",
          ["In the CI system's encrypted secrets store", "In the repository", "In the workflow file", "In the build logs"],
          "Secrets in git stay in history forever."),
        X("ci-x1", E, "Hello GitHub Actions", "GitHub Skills", "https://skills.github.com/"),
    ],
    # =============== Security ===============
    "Network Fundamentals & Security": [
        M("nt-1", E, "DNS", "What does DNS do?",
          ["Translates domain names into IP addresses", "Encrypts web traffic", "Assigns MAC addresses", "Blocks malware"],
          "It is the internet's phone book."),
        N("nt-2", MED, "Subnet size", "How many usable host addresses does a /24 IPv4 network have?", 254, 0.001,
          "256 addresses minus the network and broadcast addresses."),
        X("nt-x1", E, "Pre Security path", "TryHackMe", "https://tryhackme.com/path/outline/presecurity"),
    ],
    "Web Security & OWASP Top 10": [
        M("ws-1", E, "XSS", "What is cross-site scripting?",
          ["Injecting script that runs in another user's browser", "Guessing passwords", "Flooding a server with traffic", "Reading another site's cookies over Wi-Fi"],
          "Escape output and use a Content Security Policy."),
        M("ws-2", MED, "Stopping SQL injection", "What is the primary defence against SQL injection?",
          ["Parameterized queries", "Hiding error messages", "Longer passwords", "Client-side validation"],
          "Parameters keep data separate from the SQL code."),
        X("ws-x1", MED, "SQL injection labs", "PortSwigger Web Security Academy", "https://portswigger.net/web-security/sql-injection"),
    ],
    "Cryptography & Identity Hygiene": [
        M("cr-1", E, "Hashing vs encryption", "What is the key difference between hashing and encryption?",
          ["Hashing is one-way; encryption can be reversed with a key", "Hashing needs a key", "Encryption is one-way", "They are the same"],
          "You verify a hash; you decrypt a ciphertext."),
        M("cr-2", MED, "Public-key encryption", "To send Alice a secret with public-key cryptography, you encrypt with:",
          ["Alice's public key", "Alice's private key", "Your private key", "Your public key"],
          "Only Alice's private key can decrypt it."),
        X("cr-x1", H, "Set 1: Basics", "Cryptopals", "https://cryptopals.com/sets/1"),
    ],
    "Penetration Testing & Auditing": [
        M("pt-1", E, "Before you start", "What must exist before any penetration test begins?",
          ["Written authorization and an agreed scope", "A list of exploits", "Admin credentials", "A public announcement"],
          "Testing without permission is illegal."),
        M("pt-2", MED, "nmap -sV", "What does `nmap -sV target` add to a scan?",
          ["Detection of service versions on open ports", "A denial-of-service test", "Password guessing", "Packet capture"],
          "Versions tell you which known vulnerabilities to check."),
        X("pt-x1", MED, "Hack the Juice Shop on your own machine", "OWASP Juice Shop", "https://owasp.org/projects/juice-shop"),
    ],
    # =============== Mobile ===============
    "Mobile UI Architecture": [
        M("mu-1", E, "Long lists", "Why use FlatList or ListView.builder for 10,000 rows?",
          ["They render only the rows on screen", "They sort the rows", "They download rows faster", "They make rows clickable"],
          "Lazy rendering keeps memory use and frame times low."),
        M("mu-2", MED, "Navigation stack", "On a stack navigator, what does going back do?",
          ["Pops the top screen and reveals the one beneath", "Reloads the app", "Clears all screens", "Opens the home tab"],
          "Screens are pushed and popped like a stack."),
        X("mu-x1", E, "First codelabs", "Flutter learning pathway", "https://docs.flutter.dev/learn/pathway"),
    ],
    "State Management & Reactivity": [
        M("ms-1", E, "Single source of truth", "Two screens show the same cart. Where should the cart live?",
          ["In one shared store that both read", "Copied into each screen", "In the navigation params only", "In a global mutable variable without updates"],
          "One owner means the screens cannot disagree."),
        M("ms-2", MED, "One-way data flow", "In unidirectional data flow, how does the UI change state?",
          ["It dispatches an event or action; the store updates; the UI re-renders", "It mutates the store directly", "It edits the DOM", "It reloads the app"],
          "A single path for changes makes bugs traceable."),
        X("ms-x1", MED, "Redux Essentials tutorial app", "Redux Docs", "https://redux.js.org/tutorials/essentials/part-1-overview-concepts"),
    ],
    "REST & GraphQL Integration": [
        M("ma-1", E, "Why GraphQL", "What common REST problem does GraphQL address?",
          ["Over-fetching and under-fetching: the client asks for exactly the fields it needs", "Slow DNS", "Missing HTTPS", "Large images"],
          "One query can replace several REST calls."),
        M("ma-2", MED, "401 or 403", "A logged-in user requests another user's private data. Which status fits?",
          ["403 Forbidden", "401 Unauthorized", "404 Not Found only", "500 Internal Server Error"],
          "401 means not authenticated; 403 means authenticated but not allowed."),
        X("ma-x1", E, "Fetch and display posts in your app", "JSONPlaceholder", "https://jsonplaceholder.typicode.com/"),
    ],
    "Native Device Access & Security": [
        M("mn-1", E, "Asking for permission", "When should an app ask for camera permission?",
          ["At the moment the user starts a feature that needs the camera", "On first launch, with all other permissions", "Never", "After every restart"],
          "In-context requests are understood and accepted more often."),
        M("mn-2", MED, "Storing tokens", "Where should an auth token be stored on a phone?",
          ["In the platform's secure storage (Keychain or Keystore)", "In plain local storage", "In the app's source code", "In a public file"],
          "Secure storage is encrypted and protected by the OS."),
        X("mn-x1", H, "MAS Crackmes", "OWASP", "https://mas.owasp.org/crackmes/"),
    ],
    # =============== General software ===============
    "Software Architecture": [
        M("ar-1", E, "Single responsibility", "What does the single responsibility principle say?",
          ["A module should have one reason to change", "A class should have one method", "A file should have one line", "A team should own one service"],
          "Mixing concerns means unrelated changes collide."),
        M("ar-2", MED, "Monolith or microservices?", "For a new product with a three-person team, the usual advice is:",
          ["Start with a well-structured monolith", "Start with 20 microservices", "Avoid databases", "Write no tests until launch"],
          "Microservices add operational cost that small teams rarely need early."),
        X("ar-x1", H, "System design interview questions with solutions", "System Design Primer (GitHub)", "https://github.com/donnemartin/system-design-primer"),
    ],
    "API Integration & Web Security": [
        M("ap-1", E, "Where keys live", "Where should a third-party API secret key be kept?",
          ["In server-side environment variables or a secrets manager", "In front-end JavaScript", "In the public repository", "In the URL"],
          "Anything shipped to the browser is public."),
        M("ap-2", MED, "Rate limited", "An API replies 429 Too Many Requests. What should your client do?",
          ["Back off and retry later, honouring the Retry-After header", "Retry immediately in a loop", "Switch to a different API key", "Ignore the error"],
          "Exponential backoff protects both sides."),
        X("ap-x1", MED, "API testing labs", "PortSwigger Web Security Academy", "https://portswigger.net/web-security/api-testing"),
    ],
    "Deployment & CI/CD Pipelines": [
        M("dc-1", E, "Configuration", "Where should settings that differ between staging and production live?",
          ["In environment variables", "Hard-coded in the source", "In the README", "In commit messages"],
          "The same build should run in every environment."),
        M("dc-2", MED, "Blue-green deployment", "What is a blue-green deployment?",
          ["Running the new version beside the old one and switching traffic over, with instant rollback", "Deploying on alternate days", "Colour-coding log lines", "Testing in production only"],
          "If the new version misbehaves, switch traffic back."),
        X("dc-x1", E, "Deploy to GitHub Pages or a cloud host", "GitHub Skills", "https://skills.github.com/"),
    ],
}

_BY_ID: Dict[str, dict] = {}
_SKILL_OF: Dict[str, str] = {}
for _skill, _items in PROBLEM_BANK.items():
    for _p in _items:
        assert _p["id"] not in _BY_ID, _p["id"]
        _BY_ID[_p["id"]] = _p
        _SKILL_OF[_p["id"]] = _skill


def get_problem(problem_id: str) -> Optional[dict]:
    return _BY_ID.get(problem_id)


def skill_of(problem_id: str) -> Optional[str]:
    return _SKILL_OF.get(problem_id)


def problems_for_skill(skill_name: str) -> List[dict]:
    return PROBLEM_BANK.get(skill_name, [])


def shuffled_options(problem: dict) -> List[str]:
    """Options in a stable shuffled order (bank entries list the correct answer first)."""
    options = list(problem["options"])
    seed = int(hashlib.sha256(problem["id"].encode("utf-8")).hexdigest(), 16)
    random.Random(seed).shuffle(options)
    return options


def public_view(problem: dict, skill_name: str) -> dict:
    """What the client may see: never the answer or the explanation."""
    view = {
        "id": problem["id"], "skill_name": skill_name, "type": problem["type"],
        "difficulty": problem["difficulty"], "points": POINTS[problem["difficulty"]],
        "title": problem["title"], "prompt": problem["prompt"],
    }
    if problem["type"] == "MCQ":
        view["options"] = shuffled_options(problem)
    if problem["type"] == "EXTERNAL":
        view["platform"] = problem["platform"]
        view["url"] = problem["url"]
    return view


def grade(problem: dict, answer) -> bool:
    if problem["type"] == "MCQ":
        return isinstance(answer, str) and answer.strip() == problem["options"][0]
    if problem["type"] == "NUMERIC":
        try:
            value = float(str(answer).replace(",", "").replace("%", "").strip())
        except (TypeError, ValueError):
            return False
        return abs(value - problem["answer"]) <= problem["tolerance"] + 1e-9
    return False


def correct_answer_text(problem: dict) -> Optional[str]:
    if problem["type"] == "MCQ":
        return problem["options"][0]
    if problem["type"] == "NUMERIC":
        value = problem["answer"]
        return str(int(value)) if value == int(value) else str(value)
    return None
