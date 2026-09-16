import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.core.retriever import get_retriever
from app.core.agent import create_agent_graph
from app.core.llm import create_llm
from app.core.tools import create_tools

print("Loading...")
retriever = get_retriever()
llm = create_llm()
tools = create_tools()
agent = create_agent_graph(llm, tools)

queries = [
    "What is the fastest charger?",
    "Show me durable Type-C braided cables",
    "Are there any smartwatches under ₹2000?",
    "Best rated wireless mouse"
]

for query in queries:
    print(f"\n============================\nQuery: {query}")
    try:
        result = agent.invoke({"messages": [("user", query)]}, {"recursion_limit": 10})
        print("\nFinal Answer:\n" + result["messages"][-1].content)
    except Exception as e:
        print(f"Error: {e}")
