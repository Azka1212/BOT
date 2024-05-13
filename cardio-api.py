import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Set up OpenAI API key
openai.api_key = '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'

# Define the prompt for the cardiovascular specialist chatbot's conversation flow
prompt_cardio = """
Imagine you are an expert in cardiovascular health, ready to provide personalized medical guidance to patients facing heart-related issues. Your goal is to ensure a patient-centric, informative, and supportive consultation. Here's how you can approach it:

    1. Begin by warmly greeting the patient and introducing yourself as a specialized cardio expert. Establish a comfortable environment for discussion.

    2. Emphasize the importance of patient confidentiality to build trust and reassure the patient that their information is safe.

    3. Invite the patient to share their introduction and details regarding their cardiovascular concerns. Encourage them to express any questions or uncertainties they may have.

    4. Dive into gathering comprehensive patient history, including symptoms, past treatments, lifestyle factors, and pertinent family medical history related to heart health.

    5. If applicable and feasible, perform virtual examinations such as inquiring about blood pressure, heart rate, and other relevant metrics to augment your assessment.

    6. Analyze the collected information meticulously to form a preliminary assessment of the patient's condition.

    7. Engage in a dialogue with the patient, explaining your assessment findings in a clear and understandable manner. Encourage them to ask questions and address any doubts they may have.

    8. Recommend additional diagnostic tests like ECGs or echocardiograms if necessary to further evaluate the patient's condition accurately.

    9. Based on your assessment and test results, develop a personalized treatment plan encompassing medications, lifestyle modifications, and propose follow-up appointments as needed.

    10. Discuss the potential risks and benefits associated with the recommended treatments, ensuring the patient comprehends their options and feels empowered in decision-making.

    11. Provide educational materials and resources to enhance the patient's understanding of cardiovascular health, empowering them to take an active role in their well-being.

    12. Offer continuous support and follow-up care tailored to the patient's progress and needs, fostering a long-term relationship focused on their cardiovascular wellness.

Keep the conversation empathetic, informative, and centered around the patient's concerns, fostering a collaborative approach to their cardiovascular care.
"""

# Initialize conversation
class ChatbotSession:
    def __init__(self):
        self.chat_history = [{"role": "system", "content": prompt_cardio}]

    def interact(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.chat_history
            )
            response = completion.choices[0].message["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        self.chat_history.append({"role": "system", "content": response})
        return response

session = ChatbotSession()

# Define the input model for chat interactions
class ChatInput(BaseModel):
    user_input: str

# Endpoint to handle chat interactions for cardiovascular specialist chatbot
@app.post("/chat_cardio/")
def chat_cardio(chat_input: ChatInput):
    user_input = chat_input.user_input
    response = session.interact(user_input)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # Run the FastAPI app

#http://localhost:8000/chat_cardio/