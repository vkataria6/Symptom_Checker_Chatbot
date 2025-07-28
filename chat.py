import random
import json
import torch
import math
import geocoder

from model_chat import RNNModel
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data_rnn.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
num_layers = data["num_layers"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = RNNModel(input_size, hidden_size, output_size, num_layers).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

user_state = {"name": None, "got_symptoms": False, "asked_location": False}

def get_response(msg):
    global user_state
    sentence = tokenize(msg)

    # Detect and save name
    if user_state["name"] is None:
        if ("name" in sentence) or ("this is" in msg.lower()):
            for wor in sentence:
                if wor.lower() not in ["my", "is", "name", "i", "am", "this"]:
                    user_state["name"] = wor.capitalize()
                    return ["name", f"Thank you, {user_state['name']}. Please list the symptoms you are experiencing."]
        elif len(sentence) == 1 and sentence[0][0].isupper():
            user_state["name"] = sentence[0]
            return ["name", f"Thank you, {user_state['name']}. Please list the symptoms you are experiencing."]
        else:
            return ["not_understand", "Can you please tell me your name first?"]

    # Predict condition using RNN model
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
                response = intent["responses"]
                precaution = intent.get("Precaution", "No precautions listed.")
                return [tag, response, precaution, "Do you want to know any medical centers nearby? If yes, please provide the county and state you reside in."]
    else:
        return ["not_understand", "I'm sorry, I couldn't determine a condition from those symptoms. Could you rephrase or list them again?"]

    # Handle location input if user was asked
    if user_state.get("asked_location"):
        user_state["asked_location"] = False
        return centres(msg)

    if "yes" in sentence and "medical" in msg.lower():
        user_state["asked_location"] = True
        return centres()

    return ["not_understand", "Can you please tell me your name first?"]

def centres(location_input=None):
    with open("tri_state_medical_centers.json", "r") as json_file:
        medical_centers = json.load(json_file)

    if not location_input:
        return ["ask_location", "Do you want to know any medical centers nearby? If yes, please provide the county and state you reside in."]

    location_input = location_input.lower()
    matches = []

    for center in medical_centers["intents"]:
        address = center.get("Address", "").lower()
        if all(part.strip() in address for part in location_input.split(",")):
            matches.append(center)

    if not matches:
        return ["no_results", f"Sorry, we couldn't find medical centers in {location_input.title()}."]
    
    top_centers = matches[:3]
    response = ["center_results"]
    for center in top_centers:
        response.append([center["tag"], center["Address"]])
    return response

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print("Bot:", resp)

