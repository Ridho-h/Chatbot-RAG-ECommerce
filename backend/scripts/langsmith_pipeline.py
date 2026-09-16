"""
LangSmith Evaluation Pipeline for RAG
Creates a Golden Dataset and evaluates it using an LLM-as-a-judge (Groq).
"""
import os
import sys
import time
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field

# Ensure app imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client, evaluate
from langchain_groq import ChatGroq

from app.core.retriever import get_retriever
from app.core.agent import create_agent_graph
from app.core.llm import create_llm
from app.core.tools import create_tools

# 1. Initialize LangSmith Client
client = Client()

DATASET_NAME = "Ecommerce Golden QA"

def setup_dataset():
    """Create a golden dataset if it doesn't exist."""
    print(f"🔄 Setting up LangSmith Dataset: {DATASET_NAME}")
    

    # 4 Examples to stay within free-tier rate limits during eval
    inputs = [
        {"query": "What is the fastest charger?"},
        {"query": "Show me durable Type-C braided cables"},
        {"query": "Are there any smartwatches under ₹2000?"},
        {"query": "Best rated wireless mouse"}
    ]
    
    outputs = [
        {"answer": "The boAt Dual Port Rapid Car Charger (Qualcomm Certified) is a great fast car charger. For wall chargers, the Oraimo 18W USB & Type-C Dual Output Super Fast Charger and the iPhone Original 20W C Type Fast PD Charger are top options."},
        {"answer": "The Zoul Nylon Braided Fast Charging Type C Cable (both 1M and 2M lengths) and the Duracell Type C to Type C 5A (100W) Braided Cable are highly rated durable options."},
        {"answer": "Yes! The boAt Wave Lite (₹1,499) and the PTron Force X10 (₹1,299) are highly rated smartwatches available under ₹2000."},
        {"answer": "The Logitech B170 Wireless Mouse is the most popular best value. Other highly rated options include the HP Z3700, HP X200, and Offbeat DASH."}
    ]
    
    # In LangSmith, you can't just recreate an existing dataset by name without deleting it or updating it.
    # Since we are just testing, we'll delete the old one and recreate it.
    if client.has_dataset(dataset_name=DATASET_NAME):
        ds = client.read_dataset(dataset_name=DATASET_NAME)
        client.delete_dataset(dataset_id=ds.id)
        
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Golden Q&A pairs for the E-commerce RAG agent."
    )
    
    client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)
    print("   ✅ Created new dataset with updated golden examples.")
    return DATASET_NAME

# 2. Setup Run Function
print("\n🔄 Loading RAG components...")
retriever = get_retriever()
llm = create_llm()
tools = create_tools()
agent = create_agent_graph(llm, tools)
print("   ✅ Components loaded.")

def run_agent(inputs: dict) -> dict:
    """Wrapper function to execute the agent."""
    query = inputs["query"]
    
    # The agent might hit rate limits on Groq. Wait a bit if needed.
    time.sleep(25)
    
    print(f"\n[Agent] Answering: {query}")
    try:
        result = agent.invoke({"messages": [("user", query)]}, {"recursion_limit": 10})
        answer = result["messages"][-1].content if "messages" in result else ""
    except Exception as e:
        answer = f"Error: {str(e)}"
        
    return {"answer": answer}

# 3. Setup LLM Judge Evaluator
class Grade(BaseModel):
    reasoning: str = Field(description="Explain your reasoning for the grade in 1-2 sentences.")
    is_accurate: bool = Field(description="True if the actual response is helpful and matches the context of the expected response.")

judge = ChatGroq(model="openai/gpt-oss-20b", temperature=0).with_structured_output(Grade, method="json_mode")

async def accuracy_evaluator(run, example):
    """LLM-as-a-judge to evaluate accuracy."""
    print(f"[Evaluator] Grading response...")
    
    run_outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {}) or {}
    example_outputs = example.outputs if hasattr(example, "outputs") else example.get("outputs", {}) or {}
    
    actual = run_outputs.get("answer", "")
    expected = example_outputs.get("answer", "")
    
    prompt = f"Expected Reference Answer: {expected}\nActual Chatbot Answer: {actual}\nDoes the actual answer align with the expected context? Respond in JSON with 'is_accurate' (boolean) and 'reasoning' (string)."
    
    try:
        grade = await judge.ainvoke([{"role": "user", "content": prompt}])
        score = 1 if grade.is_accurate else 0
        comment = grade.reasoning
    except Exception as e:
        print(f"   ⚠️ Judge Error: {e}")
        score = 0
        comment = f"Evaluation failed: {str(e)}"
        
    # Another sleep to protect the evaluator calls from rate limits
    time.sleep(25)
        
    return {"key": "accuracy", "score": score, "comment": comment}

# 4. Execute Pipeline
def main():
    print("\n🚀 Starting Evaluation Pipeline")
    setup_dataset()
    
    print("\n⏳ Running evaluations... (this will take a few minutes due to rate limit pauses)")
    
    experiment_results = evaluate(
        run_agent,
        data=DATASET_NAME,
        evaluators=[accuracy_evaluator],
        experiment_prefix="Golden QA Eval",
        max_concurrency=1 # Enforce sequential to prevent Groq 429 errors
    )
    
    print(f"\n🎉 Evaluation complete! View results in LangSmith.")

if __name__ == "__main__":
    main()
