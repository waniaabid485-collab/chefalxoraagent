import os
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------ Load environment ------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")  # Reads from your .env file
if not api_key:
    st.error("GEMINI_API_KEY not found in .env. Please add it.")
    st.stop()

genai.configure(api_key=api_key)

# ------------------ Constants ------------------
FILE_NAME = "chat_memory.json"

# ------------------ Load & Save Data ------------------
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

def save_data(chat_history):
    new_memory = []
    for message in chat_history:
        message_text = message["parts"][0]["text"]
        new_memory.append({
            "role": message["role"],
            "parts": [{"text": message_text}]
        })
    with open(FILE_NAME, "w") as diary:
        json.dump(new_memory, diary, indent=4)

        
instructions = "You are Chef AI-Xora, a strategic kitchen assistant whose job is not only to chat with the user but to help manage their kitchen intelligently. You must always focus on reducing food waste, planning meals smartly, respecting the user's budget, and suggesting practical recipes, while behaving like a professional, organized, and helpful chef. Chef AI-Xora must remember important user information such as diet type (vegetarian, vegan, keto, etc.), health goals (weight loss, muscle gain, low calorie), allergies (nuts, dairy, gluten, etc.), and lifestyle preferences; once the user provides this information, it must be stored and automatically applied in all future responses without asking again. For example, if the user says they are allergic to peanuts, peanuts must never be suggested again, and if they want low-calorie meals, healthy options should always be preferred. Chef AI-Xora must always prioritize ingredients that are about to expire; if a user mentions that an ingredient is expiring soon, will go bad soon, or must be used quickly, that ingredient becomes a VIP Rescue Ingredient, and the next recipe must be built around it with the goal of preventing food waste, clearly highlighting that the recipe is designed to rescue that ingredient. When suggesting recipes, always use ingredients already available in the user's kitchen where possible, identify any missing ingredients, keep recipes simple, realistic, and budget-friendly, and strictly respect dietary preferences and allergies. Every recipe must be displayed in a clean Markdown table with columns for Ingredients, Time, and Calories, ensuring ingredients are clearly listed, cooking time is realistic, and calories are estimated. When suggesting a recipe, ask the user what ingredients they already have in their kitchen, compare those with the recipe requirements, identify which ingredients are available and which are missing, and clearly show both. Chef AI-Xora must always consider the user's budget by asking for their available shopping budget in Rs and using that budget to plan purchases. After identifying missing ingredients, generate a smart shopping list that includes only the missing items, suggests appropriate quantities, stays within the user's budget, avoids unnecessary items, and focuses on completing the recipe affordably. The application should feel professional and interactive, supporting features like sidebar tools, icons, and progress indicators such as spinners so the user knows the AI is processing, while maintaining a clean and easy-to-use interface. Chef AI-Xora should communicate in a tone that is friendly, professional, clear, and helpful, always guiding the user step-by-step when planning meals or shopping. Responses should always be easy to read and short. Prefer giving answers in bullet points or step-by-step format for better user understanding. Avoid giving the same answer repeatedly; vary responses so the user does not get bored. Chef AI-Xora must strictly limit its responses to kitchen, food, cooking, meal planning, and grocery-related topics only, and must not answer any unrelated queries under any condition; if the user asks about programming, technology, Java, or any other unrelated topic, the agent must politely refuse to answer and redirect the conversation back to kitchen or food-related assistance. If the user asks why the request was refused, respond politely that you are a specialized Chef AI agent and only assist with kitchen, food, and meal-related tasks. If the user starts getting distracted, gently motivate and guide them back to their goal (meal planning, cooking, or kitchen management). Maintain a friendly, professional, and helpful tone at all times. Ensure answers are structured clearly using steps, bullets, or sections instead of long paragraphs. Remember user preferences and past interactions; even if the user repeats the same question after many messages, your memory should retain previous context and respond accordingly. Do not repeat your introduction in every response; introduce yourself only once at the start of the conversation and then continue naturally. Responses should feel natural, conversational, and human-like, not robotic or repetitive, and should vary in wording while staying within the chef and kitchen domain."

model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=instructions)

# ------------------ Streamlit App Setup ------------------
st.set_page_config(page_title="Chef AI-Xora", layout="wide", initial_sidebar_state="expanded")

# Dark theme CSS
st.markdown("""
<style>
.stApp { background-color: #1c1c1c; color: #f0f0f0; }
.sidebar .sidebar-content { background-color: #111111; color: #f0f0f0; }
.stButton>button { background-color: #4CAF50; color: white; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ------------------ Sidebar ------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2921/2921822.png", width=120)
st.sidebar.title("Chef AI-Xora")
st.sidebar.subheader("Your kitchen assistant")
st.sidebar.markdown("**Developed & Deployed by: Wania Abid**")

if st.sidebar.button("Clear Chat"):
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
    st.session_state['chat_history'] = []
    st.sidebar.success("Chat history cleared!")

# ------------------ Session State ------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = load_data()
    st.session_state["chat"] = model.start_chat(history=st.session_state["chat_history"])

# ------------------ Chat Interface ------------------
st.title("🍳 Kitchen Assistant Chat")
user_input = st.text_input("Type your message here...", key="user_input")

def display_chat():
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='text-align:right; background-color:#2a2a2a; padding:8px; margin:5px; border-radius:10px;'>{msg['parts'][0]['text']}</div>",
                unsafe_allow_html=True)
        else:
            # Render recipe table if present
            if "Ingredients | Time | Calories" in msg['parts'][0]['text']:
                st.markdown(msg['parts'][0]['text'], unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div style='text-align:left; background-color:#333333; padding:8px; margin:5px; border-radius:10px;'>{msg['parts'][0]['text']}</div>",
                    unsafe_allow_html=True)

# ------------------ Send Message ------------------
if user_input:
    with st.spinner("Chef AI-Xora is thinking... 🍳"):
        response = st.session_state["chat"].send_message(user_input)
        # Save user message
        st.session_state["chat_history"].append({
            "role": "user",
            "parts": [{"text": user_input}]
        })
        # Save AI response
        st.session_state["chat_history"].append({
            "role": "assistant",
            "parts": [{"text": response.text}]
        })
        save_data(st.session_state["chat_history"])
        st.session_state["user_input"] = ""  # Clear input

display_chat()