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

    // Kick off first bot prompt
    this.messages.push({
      name: 'Sam',
      message: 'Hi, I am a medical chatbot. What is your age and gender?'
    });
    this.updateChatText(chatBox);
  }

  toggleState(chatbox) {
    this.state = !this.state;
    chatbox.classList.toggle('chatbox--active', this.state);
  }

  onSendButton(chatbox) {
    const textField = chatbox.querySelector('input');
    const userText = textField.value.trim();
    if (!userText) return;

    // Push user message
    this.messages.push({ name: 'User', message: userText });
    this.updateChatText(chatbox);
    textField.value = '';

    // Send to Flask
    fetch(`${window.SCRIPT_ROOT}/get_response`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText })
    })
      .then(res => res.json())
      .then(([tag, responses, extra]) => {
        // Push chatbot response(s)
        if (responses && responses.length > 0) {
          this.messages.push({ name: 'Sam', message: responses[0] });
        }
        if (extra && extra !== "") {
          this.messages.push({ name: 'Sam', message: extra });
        }
        this.updateChatText(chatbox);
      })
      .catch(err => {
        console.error("Fetch error:", err);
        this.messages.push({
          name: 'Sam',
          message: 'Sorry, something went wrong.'
        });
        this.updateChatText(chatbox);
      });
  }

  updateChatText(chatbox) {
    const container = chatbox.querySelector('.chatbox__messages > div');
    container.innerHTML = ''; // Clear

    this.messages.forEach(item => {
      const msgEl = document.createElement('div');
      const whoClass = item.name === 'Sam'
        ? 'messages__item--operator'   // bot in gray
        : 'messages__item--visitor';   // user in blue
      msgEl.classList.add('messages__item', whoClass);
      msgEl.textContent = item.message;
      container.appendChild(msgEl);
    });

    container.scrollTop = container.scrollHeight;
  }
}

const chatbox = new Chatbox();
chatbox.display();


