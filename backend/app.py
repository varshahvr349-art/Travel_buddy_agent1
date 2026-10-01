import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify , send_from_directory
from flask_cors import CORS

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain.tools import tool
from serpapi import GoogleSearch



# API KEYS


groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
serp_api_key = os.getenv("SERPAPI_KEY")



# FLASK APP


app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")

@app.route("/index.css")
def css():
    return send_from_directory("../frontend", "index.css")


@app.route("/script.js")
def javascript():
    return send_from_directory("../frontend", "script.js")

# STEP 1: INITIALIZE GROQ MODEL


model = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=groq_api_key,
    temperature=0
)



# STEP 2: CREATE DESTINATION RESEARCH TOOL


destination_research_tool = TavilySearch(
    max_results=2,
    search_depth="basic",
    tavily_api_key=tavily_api_key
)



# STEP 3: CREATE FLIGHT SEARCH TOOL


@tool
def search_flights(origin: str, destination: str, date: str) -> list:
    """Search for flights between two locations on a specified date."""

    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": date,
        "type": 2,
        "api_key": serp_api_key,
        "hl": "en",
        "gl": "in"
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    flights = []

    for flight in results.get("best_flights", [])[:5]:

        price = flight.get("price")

        total_duration = flight.get("total_duration")

        for segment in flight.get("flights", []):
            flights.append({
                "airline": segment.get("airline"),
                "flight_number": segment.get("flight_number"),
                "departure_time": segment.get("departure_airport", {}).get("time"),
                "arrival_time": segment.get("arrival_airport", {}).get("time"),
                "duration": segment.get("duration"),
                "price": price,
                "total_duration": total_duration
            })

    return flights

# STEP 4: SYSTEM PROMPT


system_prompt = """
You are TravelBuddy, an AI travel planning assistant.

Use destination_research_tool to find attractions and travel tips.
Use search_flights to find flight options.

Use IATA codes when appropriate:
HYD Hyderabad
GOI Goa
BOM Mumbai
DEL Delhi
BLR Bangalore

Give the user a concise travel plan with attractions and flights.
Do not use markdown.
"""



# STEP 5: CREATE LANGCHAIN AGENT


agent = create_agent(
    model=model,
    tools=[
        destination_research_tool,
        search_flights
    ],
    system_prompt=system_prompt
)


# STEP 6: TRAVEL API


@app.route("/travel", methods=["POST"])
def travel_buddy():

    # Get data from frontend
    data = request.get_json()

    print("Data received from frontend:")
    print(data)


    # Get travel information
    source = data.get("source")
    destination = data.get("destination")
    travel_date = data.get("travel_date")


    # Create dynamic query
    user_query = f"""
    I want to visit {destination} from {source} on {travel_date}.
    Show me top attractions and flight options.
    """


    print("User Query:")
    print(user_query)


    # Create agent message
    messages = [
        {
            "role": "user",
            "content": user_query
        }
    ]


    # Run Groq + LangChain agent
    response = agent.invoke({
        "messages": messages
    })


    # Get final AI response
    final_message = response["messages"][-1].content


    print("Final AI Response:")
    print(final_message)


    # Send AI response to frontend
    return jsonify({
        "response": final_message
    })


# STEP 7: START FLASK SERVER


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )