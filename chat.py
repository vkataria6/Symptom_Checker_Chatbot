import json
import torch
import traceback

from model_chat import RNNModel
from nltk_utils import bag_of_words, tokenize

# Device setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load intents
with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

# Load medical centers
with open("tri_state_medical_centers.json", "r") as f:
    tri_state_medical_centers = json.load(f)

# Load trained model
FILE = "data_rnn.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
num_layers = data["num_layers"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = RNNModel(input_size, hidden_size, output_size, num_layers).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

# Simple state memory
conversation_state = {
    "stage": "ask_age_gender",
    "age": None,
    "gender": None,
    "symptoms": None
}

def get_response_info(msg):
    global conversation_state
    try:
        stage = conversation_state.get("stage", "ask_age_gender")

        # === Stage 1: Ask for age and gender ===
        if stage == "ask_age_gender":
            age = None
            gender = None

            cleaned = msg.replace(",", " ").lower()
            tokens = cleaned.split()

            for token in tokens:
                if token.isnumeric():
                    age = token
                if token in ["male", "female"]:
                    gender = token

            if age and gender:
                conversation_state.update({
                    "age": age,
                    "gender": gender,
                    "stage": "ask_symptoms"
                })
                return "Bot", "Thank you. What symptoms are you experiencing?", ""

            else:
                return "Bot", "Please enter both your age and gender (e.g. 21, Female).", ""

        # === Stage 2: Classify symptoms ===
        elif stage == "ask_symptoms":
            conversation_state["symptoms"] = msg
            tag, description, precaution = classify_symptom(msg)
            conversation_state["stage"] = "ask_zip"

            diagnosis_text = f"Diagnosis: {tag}\n\nDescription: {description}"
            return "Bot", diagnosis_text, precaution or ""

        # === Stage 3: ZIP code lookup ===
        elif stage == "ask_zip":
            zip_code = msg.strip()
            conversation_state["stage"] = "done"
            centers = lookup_centers(zip_code)
            return "Bot", f"Here are the 3 closest centers near {zip_code}:\n{centers}", ""

        # === End of session ===
        else:
            return "Bot", "Thank you for using the medical chatbot!", ""

    except Exception:
        traceback.print_exc()
        return "Bot", "Sorry, something went wrong internally.", ""


def classify_symptom(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = torch.tensor(X).unsqueeze(0).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if intent["tag"] == tag:
                desc = intent.get("responses", [""])[0]
                precaution = intent.get("Precaution", "")
                return tag, desc, precaution

    return "Unknown", "I could not determine the condition. Please try rephrasing.", ""


def lookup_centers(zip_code):
    if zip_code in tri_state_medical_centers:
        centers = tri_state_medical_centers[zip_code][:3]
        return "\n".join([f"- {c['name']} ({c['address']})" for c in centers])
    return "Sorry, we couldn't find medical centers near your zip code."


def main():
    print("Chatbot active. (type 'quit' to exit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        name, message, extra = get_response_info(user_input)
        print(f"{bot_name}:", message)
        if extra:
            print(f"{bot_name}:", extra)


if __name__ == "__main__":
    main()
