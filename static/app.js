class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };

        this.state = false;
        this.messages = [];
        this.stage = "init"; // flow control
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox));
        sendButton.addEventListener('click', () => this.onSendButton(chatBox));

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        });
    }

    toggleState(chatbox) {
        this.state = !this.state;

        if (this.state) {
            chatbox.classList.add('chatbox--active');

            if (this.messages.length === 0) {
                this.messages.push({ name: "Sam", message: "Hi, I am a medical chatbot. May I know your name?" });
                this.stage = "ask_name";
                this.updateChatText(chatbox);
            }
        } else {
            chatbox.classList.remove('chatbox--active');
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value.trim();
        if (text1 === "") return;

        this.messages.push({ name: "User", message: text1 });

        if (this.stage === "ask_name") {
            this.messages.push({ name: "Sam", message: "Please list the symptoms you are experiencing" });
            this.stage = "collect_symptoms";
            this.updateChatText(chatbox);
            textField.value = '';
            return;
        }

        if (this.stage === "collect_symptoms") {
            // send to backend to get diagnosis
            fetch('http://127.0.0.1:5000/predict', {
                method: 'POST',
                body: JSON.stringify({ message: text1 }),
                mode: 'cors',
                headers: { 'Content-Type': 'application/json' },
            })
            .then(r => r.json())
            .then(r => {
                const msg = {
                    name: "Sam",
                    message1: r.answer[0],
                    message2: r.answer[1],
                    message3: r.answer[2],
                    message4: r.answer[3]
                };
                this.messages.push(msg);
                this.messages.push({ name: "Sam", message: "Do you want to know any medical centers near you?" });
                this.stage = "ask_centers";
                this.updateChatText(chatbox);
                textField.value = '';
            });
            return;
        }

        if (this.stage === "ask_centers") {
            const input = text1.toLowerCase();
            if (input.includes("no")) {
                this.messages.push({ name: "Sam", message: "Thanks for chatting!" });
                this.stage = "end";
            } else if (input.includes("yes")) {
                this.messages.push({ name: "Sam", message: "Please provide the county and state you live in." });
                this.stage = "ask_location";
            } else {
                this.messages.push({ name: "Sam", message: "Please answer yes or no." });
            }
            this.updateChatText(chatbox);
            textField.value = '';
            return;
        }

        if (this.stage === "ask_location") {
            // send location input to backend to match centers
            fetch('http://127.0.0.1:5000/predict', {
                method: 'POST',
                body: JSON.stringify({ message: text1 }),
                mode: 'cors',
                headers: { 'Content-Type': 'application/json' },
            })
            .then(r => r.json())
            .then(r => {
                let msg = {
                    name: "Sam",
                    message1: "center",
                    message2: r.answer[1],
                    message3: r.answer[2],
                    message4: r.answer[3]
                };
                this.messages.push(msg);
                this.messages.push({ name: "Sam", message: "Thanks for chatting!" });
                this.stage = "end";
                this.updateChatText(chatbox);
                textField.value = '';
            });
            return;
        }

        // fallback for all else
        this.updateChatText(chatbox);
        textField.value = '';
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item) {
            if (item.name === "Sam") {
                if (item.message1 === "center") {
                    html += '<div class="messages__item messages__item--operator">You can ask me if you want anything else.</div>'
                          + '<div class="myDIV" style="font-size: 17px;">' + item.message4[0] + ', ' + item.message4[1] + '</div>'
                          + '<div class="hide">' + item.message4[2] + '</div>'
                          + '<div class="myDIV" style="font-size: 17px;">' + item.message3[0] + ', ' + item.message3[1] + '</div>'
                          + '<div class="hide">' + item.message3[2] + '</div>'
                          + '<div class="myDIV" style="font-size: 17px;">' + item.message2[0] + ', ' + item.message2[1] + '</div>'
                          + '<div class="hide">' + item.message2[2] + '</div>'
                          + '<div class="con" style="margin-top:20px; margin-bottom:10px"><h3>Medical location that are near to you are.</h3></div>';
                } else if (item.message1) {
                    html += '<div class="messages__item messages__item--operator">Do you want to know about the nearby medical center locations</div>'
                          + '<div class="accordion" id="accordionExample">'
                          + '<div class="accordion-item" style="width: 40%; margin-top: 10px" >'
                          + '<h2 class="accordion-header" id="headingOne">'
                          + '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo">'
                          + '<b>Precautions</b></button></h2>'
                          + '<div id="collapseTwo" class="accordion-collapse collapse">'
                          + '<div class="accordion-body">' + item.message3 + '</div></div></div></div>'
                          + '<div class="accordion" id="accordionExample">'
                          + '<div class="accordion-item" style="width: 40%; margin-top: 10px" >'
                          + '<h2 class="accordion-header" id="headingThree">'
                          + '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree">'
                          + '<b>Description</b></button></h2>'
                          + '<div id="collapseThree" class="accordion-collapse collapse">'
                          + '<div class="accordion-body">' + item.message2 + '</div></div></div></div>'
                          + '<div class="messages__item messages__item--operator">Here is some more info on the disease</div>'
                          + '<div class="myDIV">' + item.message1 + '</div>'
                          + '<div class="con" style="margin-top:20px; margin-bottom:10px"><h3>This may be the possible disease that you may have.</h3></div>';
                } else {
                    html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
                }
            } else {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>';
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}

const chatbox = new Chatbox();
chatbox.display();
