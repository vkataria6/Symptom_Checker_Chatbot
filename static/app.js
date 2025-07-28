class Chatbox {
  constructor() {
    this.args = {
      openButton: document.querySelector('.chatbox__button'),
      chatBox:   document.querySelector('.chatbox__support'),
      sendButton: document.querySelector('.chatbox__send--footer')
    };
    this.state = false;
    this.messages = [];
  }

  display() {
    const { openButton, chatBox, sendButton } = this.args;

    openButton.addEventListener('click', () => this.toggleState(chatBox));

    sendButton.addEventListener('click', () => this.onSendButton(chatBox));

    const inputNode = chatBox.querySelector('input');
    inputNode.addEventListener('keyup', ({ key }) => {
      if (key === 'Enter') {
        this.onSendButton(chatBox);
      }
    });
  }

  toggleState(chatbox) {
    this.state = !this.state;
    chatbox.classList.toggle('chatbox--active', this.state);
  }

  onSendButton(chatbox) {
    const textField = chatbox.querySelector('input');
    const userText = textField.value.trim();
    if (!userText) return;

    // 1) push user message
    this.messages.push({ name: 'User', message: userText });
    this.updateChatText(chatbox);
    textField.value = '';

    // 2) call backend
    fetch(`${window.SCRIPT_ROOT}/get_response`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText })
    })
    .then(res => res.json())
    .then(([ tag, responses, precautionOrCenters ]) => {
      // tag: intent tag
      // responses: array of response strings
      // precautionOrCenters: may be string or array (centers list)
      // push bot message(s)
      this.messages.push({ name: 'Sam', message: responses[0] });
      if (precautionOrCenters) {
        this.messages.push({ name: 'Sam', message: precautionOrCenters });
      }
      this.updateChatText(chatbox);
    })
    .catch(err => {
      console.error(err);
      this.messages.push({ name: 'Sam', message: "Sorry, something went wrong." });
      this.updateChatText(chatbox);
    });
  }

  updateChatText(chatbox) {
    const container = chatbox.querySelector('.chatbox__messages > div');
    container.innerHTML = ''; // clear

    // render each message
    this.messages.forEach(item => {
      const msgEl = document.createElement('div');
      const whoClass = item.name === 'Sam'
        ? 'messages__item--operator'
        : 'messages__item--visitor';

      msgEl.classList.add('messages__item', whoClass);
      msgEl.textContent = item.message;
      container.appendChild(msgEl);
    });

    // scroll to bottom
    container.scrollTop = container.scrollHeight;
  }
}

// init
const chatbox = new Chatbox();
chatbox.display();

// kick off first prompt:
chatbox.messages.push({
  name: 'Sam',
  message: 'Hi, this is a medical chatbot. What is your age and gender?'
});
chatbox.updateChatText(chatbox.args.chatBox);