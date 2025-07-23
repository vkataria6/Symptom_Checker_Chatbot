import json
import torch

from model_chat import RNNModel  # Import the RNN model
from nltk_utils import bag_of_words, tokenize

# Device setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load JSON intents
with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

# Load JSON tri state medical centers
with open("tri_state_medical_centers.json", "r") as json_file:
    tri_state_medical_centers = json.load(json_file)

def centres():
    return tri_state_medical_centers

# Load trained model data
FILE = "data_rnn.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
num_layers = data["num_layers"]  # Number of RNN layers
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

# Initialize and load the model
model = RNNModel(input_size, hidden_size, output_size, num_layers).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

def get_response(msg):
    sentence = tokenize(msg)
    # Name extraction
    if ("name" in sentence) or ("this is" in msg.lower()):
        for wor in sentence:
            if wor.lower() not in {"my", "is", "name", "i", "am", "this"}:
                user_name = wor.capitalize()
                res = f"Hi {user_name}, please say your age."
                return ["name", res]

    # Age extraction
    if ("age" in sentence) or ("I" in sentence and "am" in sentence) or ("I'm" in sentence):
        for wor in sentence:
            if wor.isnumeric():
                user_age = wor
                res = "What is your gender?"
                return ["age", res]

    # Gender extraction
    if any(w.lower() in {"male", "female"} for w in sentence):
        for wor in sentence:
            if wor.lower() in {"male", "female"}:
                user_gender = wor.lower()
                res = "Tell the symptoms you have to know about potential conditions."
                return ["gender", res]

    # Medical center inquiry
    if ("yes" in sentence) or (("medical" in sentence) and "center" in sentence) \
       or ("hospital" in sentence) or ("hospitals" in sentence):
        return centres()

    # Fallback to RNN classification
    X = bag_of_words(sentence, all_words)
    X = torch.tensor(X).unsqueeze(0).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if intent["tag"] == tag:
                # Simple tags without precautions
                if tag in ["greeting", "goodbye", "work", "who", "Thanks", "joke", "name", "age", "gender"]:
                    return [intent['tag'], intent['responses']]
                # Tags with precautions
                return [intent['tag'], intent['responses'], intent['Precaution']]

    # If confidence is low
    return ["not_understand", "I do not understand. Can you please rephrase the sentence?"]

def main():
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence.strip().lower() == "quit":
            break

        resp = get_response(sentence)
        print("Bot:", resp)

if __name__ == "__main__":
    main()
