class Chatbox {
  constructor() {
    this.args = {
      openButton: document.querySelector('.chatbox__button'),
      chatBox: document.querySelector('.chatbox__support'),
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

    // User input: display as operator (blue bubble)
    this.messages.push({ name: 'User', message: userText });
    this.updateChatText(chatbox);
    textField.value = '';

    // Backend call
    fetch(`${window.SCRIPT_ROOT}/get_response`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText })
    })
    .then(res => res.json())
    .then(([ tag, responses, precautionOrCenters ]) => {
      // Bot response: display as visitor (gray bubble)
      this.messages.push({ name: 'Bot', message: responses[0] });
      if (precautionOrCenters) {
        this.messages.push({ name: 'Bot', message: precautionOrCenters });
      }
      this.updateChatText(chatbox);
    })
    .catch(err => {
      console.error(err);
      this.messages.push({ name: 'Bot', message: "Sorry, something went wrong." });
      this.updateChatText(chatbox);
    });
  }

  updateChatText(chatbox) {
    const container = chatbox.querySelector('.chatbox__messages > div');
    container.innerHTML = ''; // clear messages

    this.messages.forEach(item => {
      const msgEl = document.createElement('div');

      // Visitor (gray) = Bot | Operator (blue) = User
      const whoClass = item.name === 'User'
        ? 'messages__item--operator'
        : 'messages__item--visitor';

      msgEl.classList.add('messages__item', whoClass);
      msgEl.textContent = item.message;
      container.appendChild(msgEl);
    });

    // Scroll to latest message
    container.scrollTop = container.scrollHeight;
  }
}

// Init
const chatbox = new Chatbox();
chatbox.display();

// Kick off with bot prompt (gray bubble)
chatbox.messages.push({
  name: 'Bot',
  message: 'Hi, I am a medical chatbot. What is your age and gender?'
});
chatbox.updateChatText(chatbox.args.chatBox);

