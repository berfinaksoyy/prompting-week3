# Week 3 Writeup — Prompting Techniques: The Support-Desk Assistant

**Model:** llama3.1:8b, run locally with Ollama (temperature 0.0)

| Technique | Before (empty TODOs) | After (final prompt) |
|---|---|---|
| K-shot prompting | 0/4 | 4/4 |
| Chain of thought | 0/3 | 3/3 |
| Tool calling | PASS | PASS |
| RAG | 2/3 | 3/3 |

## 1. K-shot prompting

**Final prompt:**
```
You are a support ticket classifier for an online store.
Classify the customer's message into exactly one label:
billing, shipping, returns, technical, other.

Reply with ONLY the label in lowercase. No punctuation, no explanation.

Examples:
Message: I was charged the wrong amount on my invoice.
Label: billing

Message: My order still says "in transit" after ten days.
Label: shipping

Message: The jacket doesn't fit, how do I exchange it?
Label: returns

Message: I can't log in, the page keeps showing an error.
Label: technical

Message: Do you have a physical store in Istanbul?
Label: other
```

**Sample input/output:**
- Input: "My card was charged twice for order 4412."
- Before (empty prompt): "i'm so sorry to hear that your card was charged twice for order 4412. i'd be happy to help you resolve the issue..." → FAIL (0/4)
- After: `billing` → PASS (4/4)

**What I learned:** I learned that giving the model examples helps it understand the expected output. Without examples and clear instructions, it gave long responses instead of classifying tickets. After adding examples, it correctly classified all four messages.

## 2. Chain of thought

**Final prompt:**
```
You decide whether a customer's order is eligible for a refund, using the refund policy below.

Think step by step. Check each rule in order and write one short line for each:
1. Was it bought within 30 days? (yes/no)
2. Is the item unused / in original condition? (yes/no/not stated)
3. Is it a final-sale item? (yes/no/not stated)

The refund is YES only if it was bought within 30 days AND it is unused AND it is not final sale.
If any rule fails, the refund is NO.

The very last line of your answer must be exactly one of these, with nothing after it:
DECISION: YES
DECISION: NO
```

**Sample input/output:**
- Input: "Bought 45 days ago, unused."
- Before (empty prompt): the answer did not end with a `DECISION:` line, so the result could not be read (`?`) → FAIL (0/3)
- After: the model checked each rule and ended with `DECISION: NO` → PASS (3/3)

**What I learned:** I learned that breaking a decision into smaller steps helps the model follow rules more consistently. By checking each refund condition and using a fixed decision format, the model passed all three tests.

## 3. Tool calling

**Tool description:**
```
get_order_status: Look up the current status of a customer's order by its order ID.
Use this whenever the customer asks about an order.

order_id: The order number from the customer's message, digits only, e.g. 4412
```

**Final prompt:**
```
You are a support assistant for an online store.
You do not know any order details yourself.
When the customer mentions an order number, always call the get_order_status tool
with that order number before answering.
Never guess or make up an order status.
```

**Sample input/output:**
- Input: "Hi, can you check on order 4412 for me?"
- Output: tool called with `order_id='4412'` → tool result: "shipped, arriving Friday" → PASS
- Note: the check already passed before I filled in the TODOs. The tool name and the user's message were enough for the model to call the tool in this simple case.

**What I learned:** I learned that an LLM can use external tools to get information it does not already know. The test passed even without a detailed prompt, but adding clear instructions helps prevent the model from guessing order information.

## 4. RAG

**Retriever:** removes short and common words from the question, then keeps every help-center line that contains the first 5 letters of a remaining keyword (so "internationally" matches "international" and "return" matches "returns"). If nothing matches, the context is empty.

**Final prompt:**
```
You are a customer support assistant for an online store.
Answer the question using ONLY the information in the Context.
Do not use any outside knowledge and do not guess.
If the Context is empty or does not contain the answer, reply exactly:
"I'm sorry, I don't know the answer to that."
Keep your answer short (1-2 sentences).
```

**Sample input/output:**
- Input: "Do you ship internationally?"
- Before (empty retriever and prompt): "yes, we ship internationally. we strive to make our products accessible..." The check passed, but the model had no documents, so the answer was invented.
- After: "yes, we offer international shipping to most countries." → taken from help_center.txt
- Input: "What's your CEO's home address?"
- Before: "i can't provide that information..." → FAIL (the check expects a clear "don't know")
- After: "i'm sorry, i don't know the answer to that. our company's policies do not allow..." → PASS (3/3). The check passed, but the model still added an extra sentence after the required reply, so it did not follow the instruction perfectly.

**What I learned:** I learned that an LLM can give answers that sound correct even when it does not have the actual information. Using a retriever and limiting answers to the help-center document made the responses more reliable and helped the model avoid unsupported answers.

## Closing: what I learned

In this assignment, I learned how different prompting techniques can improve the behavior of an LLM. I noticed that models are good at structured tasks when they receive clear instructions, examples, and output formats. However, they can sometimes give incorrect or unnecessary information when the prompt is not specific enough. Tools and external documents help the model access information instead of guessing. Overall, I learned that good prompts and additional support are important for building reliable AI applications.