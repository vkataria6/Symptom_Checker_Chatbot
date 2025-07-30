import random
import json
import torch

import math
import geocoder

from model_chat import RNNModel  # Import the RNN model
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

# --- Updated Conversation State ---
user_state = {"name": None, "got_symptoms": False}

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
                return [tag, response, precaution, "Do you want to know about the nearby medical center locations?"]
    else:
        return ["not_understand", "I'm sorry, I couldn't determine a condition from those symptoms. Could you rephrase or list them again?"]

def centres():
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    location = geocoder.ip('me')
    given_location = location.latlng

    with open("tri_state_medical_centers.json", "r") as json_file:
        medical_centers = json.load(json_file)

    distances_to_centers = []
    for center in medical_centers["intents"]:
        center_location = center["location"]
        distance = haversine(given_location[0], given_location[1], center_location[0], center_location[1])
        distances_to_centers.append((center["tag"], distance))

    distances_to_centers.sort(key=lambda x: x[1])

    l = ["center"]
    for i, (center_name, distance) in enumerate(distances_to_centers[:5], start=1):
        for center in medical_centers["intents"]:
            if center["tag"] == center_name:
                l.append([center_name, f"{round(distance, 2)}km", center["Address"]])
    return l

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print("Bot:", resp)
