

import base64, io, os, re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

CSV_PATH = os.path.join(os.path.dirname(__file__), "titanic.csv")
df = pd.read_csv(CSV_PATH)
df.columns = [c.strip().lower() for c in df.columns]

HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
LLM_TIMEOUT = 15  
try:
    llm = HuggingFaceEndpoint(
        repo_id=HF_MODEL,
        huggingfacehub_api_token=HF_TOKEN,
        temperature=0.1,
        max_new_tokens=256,
        timeout=LLM_TIMEOUT,
    )
except Exception as e:
    print("Warning: HuggingFaceEndpoint init failed:", e)
    llm = None

RESPONSE_PROMPT = PromptTemplate.from_template(
    """You are a friendly Titanic dataset analyst chatbot. The user asked a question
and you have already computed the answer. Restate the result clearly and concisely
in 1-3 sentences. Do not add information you are not given.

Dataset: 891 Titanic passengers with columns — survived, pclass, sex, age,
sibsp, parch, fare, embarked, class, who, adult_male, deck, embark_town, alive, alone.

User question: {question}
Computed result: {result}

Your response:"""
)

response_chain = None
if llm is not None:
    try:
        response_chain = RESPONSE_PROMPT | llm | StrOutputParser()
    except Exception as e:
        print("Warning: response_chain construction failed:", e)
        response_chain = None


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor="#f8f9fa", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def _styled_fig(figsize=(9, 5)):
    sns.set_theme(style="whitegrid", palette="muted")
    return plt.subplots(figsize=figsize)


def _male_percentage():
    pct = df["sex"].value_counts(normalize=True)["male"] * 100
    return f"{pct:.2f}% of passengers were male.", None

def _female_percentage():
    pct = df["sex"].value_counts(normalize=True)["female"] * 100
    return f"{pct:.2f}% of passengers were female.", None

def _avg_fare():
    avg = df["fare"].mean()
    return f"The average ticket fare was £{avg:.2f}. Median fare was £{df['fare'].median():.2f}.", None

def _avg_age():
    avg = df["age"].dropna().mean()
    return f"The average passenger age was {avg:.1f} years (median {df['age'].dropna().median():.1f}).", None

def _survival_count():
    survived = df["survived"].sum()
    total = len(df)
    rate = survived / total * 100
    return f"{survived} out of {total} passengers survived ({rate:.1f}% survival rate).", None

def _total_passengers():
    return f"There were {len(df)} total passengers on the Titanic.", None

def _age_histogram():
    fig, ax = _styled_fig()
    sns.histplot(df["age"].dropna(), bins=30, kde=True, color="#4e79a7", ax=ax)
    ax.set_title("Distribution of Passenger Ages", fontsize=14, fontweight="bold")
    ax.set_xlabel("Age")
    ax.set_ylabel("Count")
    plt.tight_layout()
    avg = df["age"].dropna().mean()
    text = (f"Here's the age distribution. Average age: {avg:.1f} years, "
            f"youngest: {df['age'].min():.1f}, oldest: {df['age'].max():.1f}.")
    return text, _fig_to_base64(fig)

def _fare_histogram():
    fig, ax = _styled_fig()
    sns.histplot(df["fare"].dropna(), bins=40, kde=True, color="#e15759", ax=ax)
    ax.set_title("Distribution of Ticket Fares", fontsize=14, fontweight="bold")
    ax.set_xlabel("Fare (£)")
    ax.set_ylabel("Count")
    plt.tight_layout()
    return (f"Here's the fare distribution. Average fare: £{df['fare'].mean():.2f}, "
            f"max: £{df['fare'].max():.2f}."), _fig_to_base64(fig)

def _embark_chart():
    fig, ax = _styled_fig()
    counts = df["embark_town"].value_counts()
    colors = ["#4e79a7", "#f28e2b", "#e15759"]
    counts.plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Passengers by Embarkation Port", fontsize=14, fontweight="bold")
    ax.set_xlabel("Port")
    ax.set_ylabel("Number of Passengers")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    lines = ["Passengers by embarkation port:"]
    for port, count in counts.items():
        lines.append(f"  • {port}: {count}")
    return "\n".join(lines), _fig_to_base64(fig)

def _class_chart():
    fig, ax = _styled_fig()
    counts = df["class"].value_counts()
    colors = ["#4e79a7", "#f28e2b", "#e15759"]
    counts.plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Passengers by Class", fontsize=14, fontweight="bold")
    ax.set_xlabel("Class")
    ax.set_ylabel("Count")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    lines = ["Passengers by class:"]
    for cls, count in counts.items():
        lines.append(f"  • {cls}: {count}")
    return "\n".join(lines), _fig_to_base64(fig)

def _survival_by_gender():
    fig, ax = _styled_fig()
    rates = df.groupby("sex")["survived"].mean() * 100
    colors = ["#4e79a7", "#e15759"]
    rates.plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Survival Rate by Gender", fontsize=14, fontweight="bold")
    ax.set_xlabel("Gender")
    ax.set_ylabel("Survival Rate (%)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    lines = ["Survival rate by gender:"]
    for gender, rate in rates.items():
        lines.append(f"  • {gender}: {rate:.1f}%")
    return "\n".join(lines), _fig_to_base64(fig)

def _survival_by_class():
    fig, ax = _styled_fig()
    rates = df.groupby("class")["survived"].mean() * 100
    colors = ["#4e79a7", "#f28e2b", "#e15759"]
    rates.plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Survival Rate by Class", fontsize=14, fontweight="bold")
    ax.set_xlabel("Class")
    ax.set_ylabel("Survival Rate (%)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    lines = ["Survival rate by class:"]
    for cls, rate in rates.items():
        lines.append(f"  • {cls}: {rate:.1f}%")
    return "\n".join(lines), _fig_to_base64(fig)

def _age_by_class():
    fig, ax = _styled_fig()
    sns.boxplot(data=df, x="class", y="age", palette="muted", ax=ax)
    ax.set_title("Age Distribution by Class", fontsize=14, fontweight="bold")
    plt.tight_layout()
    means = df.groupby("class")["age"].mean()
    lines = ["Average age by class:"]
    for cls, avg in means.items():
        lines.append(f"  • {cls}: {avg:.1f} years")
    return "\n".join(lines), _fig_to_base64(fig)

def _fare_by_class():
    fig, ax = _styled_fig()
    sns.boxplot(data=df, x="class", y="fare", palette="muted", ax=ax)
    ax.set_title("Fare Distribution by Class", fontsize=14, fontweight="bold")
    plt.tight_layout()
    means = df.groupby("class")["fare"].mean()
    lines = ["Average fare by class:"]
    for cls, avg in means.items():
        lines.append(f"  • {cls}: £{avg:.2f}")
    return "\n".join(lines), _fig_to_base64(fig)

def _general_stats():
    """Fallback: provide a general dataset overview."""
    survived = df["survived"].sum()
    total = len(df)
    text = (
        f"Titanic Dataset Overview ({total} passengers):\n"
        f"  • Survived: {survived} ({survived/total*100:.1f}%)\n"
        f"  • Male: {(df['sex']=='male').sum()}, Female: {(df['sex']=='female').sum()}\n"
        f"  • Average age: {df['age'].dropna().mean():.1f} years\n"
        f"  • Average fare: £{df['fare'].mean():.2f}\n"
        f"  • Embarked from: {', '.join(f'{k} ({v})' for k, v in df['embark_town'].value_counts().items())}\n"
        f"  • Classes: {', '.join(f'{k} ({v})' for k, v in df['class'].value_counts().items())}"
    )
    return text, None


INTENT_MAP = [
 
    (["age"], ["histogram", "distribution", "chart", "plot", "show", "graph"], _age_histogram),
    (["fare"], ["histogram", "distribution", "chart", "plot", "show", "graph"], _fare_histogram),
    ([], ["embark", "port"], _embark_chart),
    (["class"], ["how many", "count", "chart", "plot", "show", "distribution", "number"], _class_chart),
    (["surviv"], ["gender", "sex", "male", "female", "chart", "plot", "bar", "rate", "show"], _survival_by_gender),
    (["surviv"], ["class", "pclass"], _survival_by_class),
    (["age"], ["class", "box"], _age_by_class),
    (["fare"], ["class", "box"], _fare_by_class),
    (["male"], ["percent", "%", "proportion", "ratio"], _male_percentage),
    (["female"], ["percent", "%", "proportion", "ratio"], _female_percentage),
    (["fare"], ["average", "mean", "avg"], _avg_fare),
    (["age"], ["average", "mean", "avg"], _avg_age),
    (["surviv"], [], _survival_count),
    (["total", "passenger"], [], _total_passengers),
]


def _detect_and_run(question: str):
    q = question.lower()

    OUT_OF_SCOPE_KEYWORDS = {
        "alien", "aliens", "ufo", "unicorn", "dog", "dogs", "cat", "cats",
        "gdp", "weather", "stock", "stocks", "bitcoin", "president", "prime minister",
        "population", "currency", "vacation", "concert", "score", "match",
        "netflix", "movie", "who won", "who is", "married", "marriage", "birth", "death (year)",
        "mars", "moon", "dinosaurs", "planet", "spacecraft", "covid", "pandemic"
    }
    for term in OUT_OF_SCOPE_KEYWORDS:
        if term in q:
            return (
                f"Sorry — that question appears unrelated to the Titanic passenger dataset (found term '{term}'). "
                "I can answer data questions about passengers (columns like age, sex, survived, pclass, fare, embarked, class, etc.). "
                "Try: 'What percentage of passengers were male?' or 'Show me a histogram of passenger ages'.",
                None,
            )

    for kw_all, kw_any, handler in INTENT_MAP:
        try:
            if all(k in q for k in kw_all):
                if not kw_any or any(k in q for k in kw_any):
                    try:
                        return handler()
                    except Exception as e:
                        print(f"Handler {handler.__name__} raised:", e)
                        return (f"Sorry — I couldn't compute the requested chart/stat due to an internal error.", None)
        except Exception as e:
            print("Error during intent check:", e)

    try:
        return _general_stats()
    except Exception as e:
        print("Error in general_stats:", e)
        return ("Sorry — cannot produce dataset overview due to an internal error.", None)


def process_query(question: str) -> dict:
    """Answer a natural-language question about the Titanic dataset.

    Returns {"answer": str, "plot": str | None}
    """
    if not question or not isinstance(question, str):
        return {"answer": "Please ask a clear question about the Titanic dataset.", "plot": None}

    try:
        raw_result, plot = _detect_and_run(question)
    except Exception as e:
        print("Error while running intent detection:", e)
        raw_result, plot = ("Sorry — I encountered an internal error while processing your question.", None)

    if raw_result is None:
        raw_result = "No result computed."
    else:
        raw_result = str(raw_result)

    answer = raw_result
    try:
        if HF_TOKEN and response_chain is not None:
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        response_chain.invoke,
                        {"question": question, "result": raw_result},
                    )
                    polished = future.result(timeout=LLM_TIMEOUT)
                    if isinstance(polished, str):
                        polished = polished.strip()
                    else:
                        polished = str(polished).strip()

                if polished and 10 < len(polished) < 2000:
                    answer = polished
                else:
                    answer = raw_result

            except FuturesTimeout:
                print("LLM polishing timed out; returning raw computed result.")
                answer = raw_result
            except Exception as e:
                print("LLM polishing failed:", e)
                answer = raw_result
        else:
            if not HF_TOKEN:
                print("Hugging Face token not found — skipping LLM polishing.")
            if response_chain is None:
                print("response_chain not available — skipping LLM polishing.")
            answer = raw_result

    except Exception as e:
        print("Unexpected error during LLM polishing:", e)
        answer = raw_result

    try:
        low = question.lower()
        if any(w in low for w in ["alien", "aliens", "ufo", "unicorn", "dinosaurs"]):
            return {
                "answer": "That question appears to assume facts outside this dataset (e.g., 'aliens'). I can only answer questions about the Titanic passenger dataset. Try asking about age, fare, sex, survival, class, or embarkation.",
                "plot": None,
            }
    except Exception:
        pass

    return {"answer": answer, "plot": plot}