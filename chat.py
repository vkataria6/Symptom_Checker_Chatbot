import json
import torch
from model_chat import RNNModel
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load data
with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

with open("tri_state_medical_centers.json", "r") as json_file:
    tri_state_medical_centers = json.load(json_file)

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

# Conversation state memory
user_context = {
    "name": None,
    "age": None,
    "gender": None,
    "symptom_tag": None,
    "got_prognosis": False,
    "county": None,
    "state": None
}

def get_response(msg):
    global user_context

    sentence = tokenize(msg)

    # Step 1: Get Name
    if user_context["name"] is None:
        for w in sentence:
            if w.lower() not in {"my", "name", "is", "i", "am", "this", "hi", "hello"}:
                user_context["name"] = w.capitalize()
                return ["name", f"Hi {user_context['name']}, how old are you?"]

    # Step 2: Get Age
    if user_context["age"] is None:
        for w in sentence:
            if w.isnumeric():
                user_context["age"] = int(w)
                return ["age", "What is your gender (male/female)?"]

    # Step 3: Get Gender
    if user_context["gender"] is None:
        for w in sentence:
            if w.lower() in {"male", "female"}:
                user_context["gender"] = w.lower()
                return ["gender", "Tell me the symptoms you are experiencing."]

    # Step 4: Detect symptom tag using model
    if not user_context["got_prognosis"]:
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
                    user_context["symptom_tag"] = tag
                    user_context["got_prognosis"] = True
                    response = intent["responses"][0]
                    precaution = intent.get("Precaution", "")
                    return [tag, response, precaution]
        else:
            return ["low_confidence", "I'm not sure what you mean. Could you rephrase the symptoms?"]

    # Step 5: Ask for county and state
    if user_context["county"] is None or user_context["state"] is None:
        for w in sentence:
            w = w.replace(",", "")
        tokens = sentence
        for i in range(len(tokens) - 1):
            if tokens[i].lower().endswith("county"):
                user_context["county"] = tokens[i].title()
                user_context["state"] = tokens[i + 1].title()
                break

        if user_context["county"] and user_context["state"]:
            # Match county and state
            county = user_context["county"]
            state = user_context["state"]
            key = f"{county}, {state}"

            if key in tri_state_medical_centers:
                centers = tri_state_medical_centers[key]
                if centers:
                    response = f"Here are some nearby medical centers in {key}:\n"
                    for center in centers[:3]:
                        response += f"• {center['name']} ({center['address']})\n"
                    return ["centers", response]
                else:
                    return ["no_centers", f"Sorry, we couldn't find medical centers in {key}."]
            else:
                return ["no_match", "Could you recheck the county and state name?"]
        else:
            return ["ask_location", "Please provide the county and state you reside in (e.g., 'Queens County, NY')."]

    return ["done", "Thank you for using the symptom checker!"]

# For terminal testing
if __name__ == "__main__":
    print("Bot is running. Type 'quit' to exit.")
    while True:
        text = input("You: ")
        if text.lower() == "quit":
            break
        response = get_response(text)
        print("Bot:", response)
