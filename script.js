const backendURL = "/api/chat";

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  speechSynthesis.speak(utterance);
}

function startListening() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

  recognition.start();

  recognition.onresult = async (event) => {
    const text = event.results[0][0].transcript;

    const res = await fetch(backendURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();

    speak(data.response);
  };
}