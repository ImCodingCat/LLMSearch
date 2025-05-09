import streamlit as st
import os

from google import genai
from google.genai import types
from apify_client import ApifyClient

from dotenv import load_dotenv

load_dotenv()
# Made by Muhammad Dava Pasha
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
apify_client = ApifyClient(APIFY_API_KEY)

# Define google map search tool calling

prompt = ""

def GoogleMapSearch(searchString: list[str], location: str):
    """Returns google map search result in object below
    place_name = The place name
    total_score = The total score of that place
    reviewsCount = How many given reviews
    url = The url where user can click

    Please format them in markdown for easy to read and always include the url in response!

    Args:
      searchString: Type what you’d normally search for in the Google Maps search bar, like English breakfast or pet shelter. Aim for unique terms for faster processing. Using similar terms (e.g., bar vs. restaurant vs. cafe) may slightly increase your capture rate but is less efficient.
      location: Define location using free text. Simpler formats work best; e.g., use City + Country rather than City + Country + State.
    """
    run_input = {
        "searchStringsArray": searchString,
        "locationQuery": location,
        "maxCrawledPlacesPerSearch": 10,
        "language": "en",
        "searchMatching": "all",
        "placeMinimumStars": "",
        "website": "allPlaces",
        "skipClosedPlaces": False,
        "scrapePlaceDetailPage": False,
        "scrapeTableReservationProvider": False,
        "includeWebResults": False,
        "scrapeDirectories": False,
        "maxQuestions": 0,
        "scrapeContacts": False,
        "maxReviews": 0,
        "reviewsSort": "newest",
        "reviewsFilterString": "",
        "reviewsOrigin": "all",
        "scrapeReviewsPersonalData": True,
        "maxImages": 0,
        "scrapeImageAuthors": False,
        "allPlacesNoSearchAction": "",
    }

    run = apify_client.actor("nwua9Gu5YrADL7ZDj").call(run_input=run_input)

    result = []
    for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
        result.append({
            "place_name": item["title"],
            "total_score": item["totalScore"],
            "reviewsCount": item["reviewsCount"],
            "url": item["url"]
        })

    return result


def generateChat():
    response = client.models.generate_content_stream(
        model = "gemini-2.0-flash",
        contents = prompt,
        config=types.GenerateContentConfig(tools=[GoogleMapSearch])
    )
    
    for chunk in response:
        yield chunk.text

st.title("LLM Search made By Muhammad Dava Pasha")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can i help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(generateChat)


    st.session_state.messages.append({"role": "assistant", "content": response})
