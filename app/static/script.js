const toggleRunPauseButton = document.getElementById("toggleRunPause");
const resetQueryCountButton = document.getElementById("resetQueryCount");
const messagesList = document.getElementById("messages");
const currentHypothesisParagraph = document.getElementById("currentHypothesis");

const ws1 = new WebSocket("ws://127.0.0.1:8000/ws/agent1");
const ws2 = new WebSocket("ws://127.0.0.1:8000/ws/agent2");

ws1.onmessage = (event) => {
    updateChat(event.data);
};

ws2.onmessage = (event) => {
    updateChat(event.data);
};

function updateChat(data) {
    const parsedData = JSON.parse(data);
    const conversation = parsedData.conversation;
    const currentHypothesis = parsedData.current_hypothesis;

    messagesList.innerHTML = "";
    conversation.forEach((msg) => {
        const li = document.createElement("li");
        li.textContent = `${msg.agent}: ${msg.content}`;
        messagesList.appendChild(li);
    });

    currentHypothesisParagraph.textContent = currentHypothesis.content;
}

toggleRunPauseButton.addEventListener("click", async () => {
    const response = await fetch("/toggle_run_pause");
    const data = await response.json();
    toggleRunPauseButton.textContent = data.run_pause_state ? "Pause" : "Run";
});

resetQueryCountButton.addEventListener("click", async () => {
    const response = await fetch("/reset_query_count");
    const data = await response.json();
    alert(`Query count reset to ${data.current_query_count}`);
});