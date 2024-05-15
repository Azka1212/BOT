import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import pickle

import uvicorn

app = FastAPI()

# Set up OpenAI API key
openai.api_key = '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'

# Define the prompt for the chatbot's conversation flow
prompt = """
Act as an expert clinical psychiatrist to talk to patients with mental health issues in order to accurately diagnose their problems by performing the following steps one by one:
1. Greet the patient and introduce yourself as a chatbot trained to help people through their mental health issues.
2. Make it clear that the information shared here will remain confidential.
3. Ask for the patient’s introduction.
4. Get to know the patient by initiating small talk with simple questions like:
   - How is your day going?
   - How have you been?
   - How are you feeling?
   - Is there anything bothering you? Would you like to share how you are coping with it?
5. Keep asking questions to dive deeper into your patient’s mental state until the patient has given you enough information for an accurate diagnosis.
6. Once you have a diagnosis, probe the patient with questions to confirm if their symptoms match the mental health issue you have identified. Then, use academic literature and the most credible and updated sources of information in the field of clinical psychiatry to identify and confirm the diagnosis.
7. As kindly as possible, explain the mental health issue to the patient and answer all the questions they may have regarding their diagnosis before recommending sources like credible textbooks or papers for further reading.
8. Lastly, conduct thorough research on the identified issue to create a comprehensive step-by-step plan for the patient’s treatment, which must include usually prescribed medication and mental and physical exercises to treat the identified issue along with reasoning and evidence from credible sources to support the prescribed steps for treatment.
9. Then, ask the patient if they would like to share their thoughts on the diagnosis or if they have any other questions.
10. Lastly, thank the patient for their time and wish them a quick recovery and a good day ahead.

Keep in mind that you need to act like an actual clinical psychiatrist who knows how to ease the patient into sharing enough info for the diagnosis by keeping the conversation flowing with one question at a time instead of overwhelming the patient with a lot of information in one output.
"""

# Define the UserSession class to manage chat sessions
class UserSession:
    def __init__(self, user_name):
        self.user_name = user_name
        self.chat_history = [{"role": "assistant", "content": prompt}]  # Initialize chat history with the prompt

    def save_chat_message(self, message):
        self.chat_history.append({"role": "assistant", "content": message})  # Save chat messages to the history

    def chat_interaction(self, response):
        if response.lower() == "exit":
            return {"response": "Session ended. Thank you for your time."}  # End the session if user input is 'exit'

        self.chat_history.append({"role": "user", "content": response})  # Save user input to the chat history

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.chat_history
            )
            latest_response = completion.choices[0].message["content"]  # Get the latest chatbot's response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        self.save_chat_message(latest_response)  # Save the latest chatbot's response to the history

        return {"response": latest_response}  # Return only the latest chatbot response

sessions_file = "sessions.pkl"

# Function to load user sessions from a pickle file
def load_sessions():
    if not os.path.exists(sessions_file):
        return {}  # Return an empty dictionary if sessions file doesn't exist
    
    with open(sessions_file, 'rb') as f:
        return pickle.load(f)

# Function to save user sessions to a pickle file
def save_sessions(sessions):
    with open(sessions_file, 'wb') as f:
        pickle.dump(sessions, f)

sessions = load_sessions()

# Define the input model for chat interactions
class ChatInput(BaseModel):
    response: str
    user_name: Optional[str] = None

# Endpoint to start a new chat session for a user
@app.post("/start_session/")
def start_session(user_input: str):
    if user_input not in sessions:
        sessions[user_input] = UserSession(user_input)  # Create a new UserSession if user not in sessions
        save_sessions(sessions)  # Save sessions to file
        return {"message": f"Session started for user: {user_input}"}
    else:
        return {"message": f"Session found for user: {user_input}"}

# Endpoint to handle chat interactions during a session
@app.post("/chat_interaction/")
def chat_interaction(chat_input: ChatInput):
    user_name = chat_input.user_name
    response = chat_input.response  # Updated variable name from user_input to response

    if user_name not in sessions:
        sessions[user_name] = UserSession(user_name)  # Create a new session if user not in sessions
    else:
        session = sessions[user_name]
        return session.chat_interaction(response)  # Updated variable name from user_input to response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # Run the FastAPI app
