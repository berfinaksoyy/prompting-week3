"""RAG — policy-grounded answers.

Task: answer a customer question using ONLY the retrieved help-center text. If the
answer isn't in the docs, the model must say it doesn't know (don't hallucinate).

Fill in YOUR_SYSTEM_PROMPT and YOUR_RETRIEVER.
Run:  python rag.py
"""
import os

from ollama import chat

MODEL = "llama3.1:8b"
DATA = os.path.join(os.path.dirname(__file__), "data", "help_center.txt")


def load_chunks() -> list[str]:
    with open(DATA, encoding="utf-8") as f:
        # one chunk per non-empty line
        return [line.strip() for line in f if line.strip()]
STOPWORDS = {"what", "whats", "your", "you", "how", "long", "have", "does", "with",
             "the", "for", "and", "can", "are", "will", "this", "that", "from"}


# Retriever: keep the help-center lines that share a keyword with the question.
def YOUR_RETRIEVER(question: str, chunks: list[str]) -> list[str]:
    words = [w.strip("?.,!'\"").lower() for w in question.split()]
    keywords = [w for w in words if len(w) > 3 and w not in STOPWORDS]
    results = []
    for chunk in chunks:
        text = chunk.lower()
        for word in keywords:
            # match "ship" with "shipping", "return" with "returns", etc.
            if word[:5] in text:
                results.append(chunk)
                break
    return results


YOUR_SYSTEM_PROMPT = """You are a customer support assistant for an online store.
Answer the question using ONLY the information in the Context.
Do not use any outside knowledge and do not guess.
If the Context is empty or does not contain the answer, reply exactly:
"I'm sorry, I don't know the answer to that."
Keep your answer short (1-2 sentences)."""

CASES = [
    ("How long do I have to return an item?", ["30 days"]),
    ("Do you ship internationally?", ["international"]),
    ("What's your CEO's home address?", ["don't know", "do not know", "not sure", "cannot"]),
]


def answer(question: str) -> str:
    context = "\n".join(YOUR_RETRIEVER(question, load_chunks()))
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": YOUR_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        options={"temperature": 0.0},
    )
    return resp.message.content.strip().lower()


def run() -> bool:
    passed = 0
    for question, needles in CASES:
        got = answer(question)
        ok = any(n.lower() in got for n in needles)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {question!r} -> {got[:80]!r}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
