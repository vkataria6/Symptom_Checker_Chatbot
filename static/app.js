class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))
        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;
        if (this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            let msg2 = {name: "Sam", message1: r.answer[0], message2: r.answer[1], message3: r.answer[2], message4: r.answer[3]}
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''
        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
        });
    }

    updateChatText(chatbox) {
        var html = '';
        const specificTags = ["greeting", "goodbye", "work", "who", "Thanks", "joke", "name", "age", "gender", "not_understand"]

        this.messages.slice().reverse().forEach(function(item) {
            if (item.name === "Sam") {

                if (specificTags.includes(item.message1)) {
                    html += '<div class="messages__item messages__item--visitor">' + item.message2 + '</div>';
                }

                else if (item.message1 === "center_results") {
                    html += '<div class="con" style="margin-top:20px; margin-bottom:10px"><h3>Medical centers near you:</h3></div>';
                    for (let i = 0; i < item.message2.length; i++) {
                        html += '<div class="myDIV" style="font-size: 17px;">' + item.message2[i][0] + '</div>';
                        html += '<div class="hide">' + item.message2[i][1] + '</div>';
                    }
                    html += '<div class="messages__item messages__item--visitor">You can ask me anything else.</div>';
                }

                else {
                    html += '<div class="messages__item messages__item--visitor">Do you want to know about the nearby medical center locations? If so, please provide the nearest city from you.</div>'
                        + '<div class="accordion" id="accordionExample">'
                            + '<div class="accordion-item" style="width: 40%; margin-top: 10px" >'
                            + '<h2 class="accordion-header" id="headingOne">'
                            + '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">'
                            + '<b>Precautions</b>'
                            + '</button>'
                            + '</h2>'
                            + '<div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#accordionExample">'
                            + '<div class="accordion-body">' + item.message3 + '</div>'
                            + '</div></div></div>'
                        + '<div class="accordion" id="accordionExample">'
                            + '<div class="accordion-item" style="width: 40%; margin-top: 10px" >'
                            + '<h2 class="accordion-header" id="headingThree">'
                            + '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">'
                            + '<b>Description</b>'
                            + '</button>'
                            + '</h2>'
                            + '<div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#accordionExample">'
                            + '<div class="accordion-body">' + item.message2 + '</div>'
                            + '</div></div></div>'
                        + '<div class="messages__item messages__item--visitor">Here is some more info on the disease</div>'
                        + '<div class="myDIV">' + item.message1 + '</div>'
                        + '<div class="con" style="margin-top:20px; margin-bottom:10px"><h3>This may be the possible disease that you may have.</h3></div>';
                }

            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
            }
        });

        html += '<div class="messages__item messages__item--visitor">Hi, this is a medical chat support. May I know your name? </div>';

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}

const chatbox = new Chatbox();
chatbox.display();

