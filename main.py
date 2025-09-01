import time
from dotenv import load_dotenv
from typing import List, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from web_operations import serp_search
# from .visualize import export_graph_visualizations

load_dotenv()


def get_llm() -> ChatGroq:
    """Lazily construct the LLM when needed by nodes, avoiding init at import time."""
    return ChatGroq(model="deepseek-r1-distill-llama-70b")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_question: str | None
    google_results: list | None
    bing_results: list | None
    reddit_results: list | None
    selected_reddit_urls: list[str] | None
    reddit_post_data: list | None
    google_analysis: str | None
    bing_analysis: str | None
    reddit_analysis: str | None
    final_answer: str | None


def google_search(state: State):
    user_question = state.get("user_question", "")
    print(f"Searching Google for: {user_question}")

    google_results = serp_search(user_question, engine="google")
    print(google_results)

    return {"google_results": google_results}

def bing_search(state: State):
    user_question = state.get("user_question", "")
    print(f"Searching Bing for: {user_question}")

    bing_results = serp_search(user_question, engine="bing")
    print(bing_results)

    return {"bing_results": bing_results}

def reddit_search(state: State):
    user_question = state.get("user_question", "")
    print(f"Searching Reddit for: {user_question}")

    time.sleep(2)

    reddit_results = []

    return {"reddit_results": reddit_results}


def retrieve_reddit_posts(state: State):
    return {"reddit_post_data": []}

def analyze_reddit_posts(state: State):
    return {"selected_reddit_urls": []}

def analyze_google_results(state: State):
    return {"google_analysis": ""}

def analyze_bing_results(state: State):
    return {"bing_analysis": ""}

def analyze_reddit_results(state: State):
    return {"reddit_analysis": ""}

def synthesize_analysis(state: State):
    return {"final_answer": ""}


graph_builder = StateGraph(State)

graph_builder.add_node("google_search", google_search)
graph_builder.add_node("bing_search", bing_search)
graph_builder.add_node("reddit_search", reddit_search)
graph_builder.add_node("retrieve_reddit_posts", retrieve_reddit_posts)
graph_builder.add_node("analyze_reddit_posts", analyze_reddit_posts)
graph_builder.add_node("analyze_google_results", analyze_google_results)
graph_builder.add_node("analyze_bing_results", analyze_bing_results)
graph_builder.add_node("analyze_reddit_results", analyze_reddit_results)
graph_builder.add_node("synthesize_analysis", synthesize_analysis)

graph_builder.add_edge(START, "google_search")
graph_builder.add_edge(START, "bing_search")
graph_builder.add_edge(START, "reddit_search")

graph_builder.add_edge("google_search", "analyze_reddit_posts")
graph_builder.add_edge("bing_search", "analyze_reddit_posts")
graph_builder.add_edge("reddit_search", "analyze_reddit_posts")

graph_builder.add_edge("analyze_reddit_posts", "retrieve_reddit_posts")

graph_builder.add_edge("retrieve_reddit_posts", "analyze_google_results")
graph_builder.add_edge("retrieve_reddit_posts", "analyze_bing_results")
graph_builder.add_edge("retrieve_reddit_posts", "analyze_reddit_results")

graph_builder.add_edge("analyze_google_results", "synthesize_analysis")
graph_builder.add_edge("analyze_bing_results", "synthesize_analysis")
graph_builder.add_edge("analyze_reddit_results", "synthesize_analysis")

graph_builder.add_edge("synthesize_analysis", END)

graph = graph_builder.compile()

def run_chatbot():
    print("Multi-source Research Agent")
    print("Enter 'quit' to exit\n")

    while True:
        user_input = input("Ask me anything: ")
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        
        state = {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "user_question": user_input,
            "google_results": None,
            "bing_results": None,
            "reddit_results": None,
            "selected_reddit_urls": None,
            "reddit_post_data": None,
            "google_analysis": None,
            "bing_analysis": None,
            "reddit_analysis": None,
            "final_answer": None
        }

        print("\n Starting parellel research process...\n")
        print("Launching Google, Bing, and Reddit searches...\n")
        
        final_state = graph.invoke(state)
        if final_state.get("final_answer"):
            print(f"\n Final Answer: {final_state.get('final_answer')}\n")
        
        print("-" * 80)


if __name__ == "__main__":
    run_chatbot()