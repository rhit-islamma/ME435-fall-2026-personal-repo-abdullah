async function sendCommand(command) {
    var response = await fetch(`/api/${command}`);
    var replyText = await response.text();
    console.log(replyText);

    document.querySelector("#replyText").innerHTML = replyText;
}

function main() {
    document.querySelector("#ledOn").onclick = () => {
        sendCommand("led/on");
    }

    document.querySelector("#ledOff").onclick = () => {
        sendCommand("led/off");
    }

    document.querySelector("#flash").onclick = () => {
        var numFlashes = document.querySelector("#numFlashes").value;
        var periodMs = document.querySelector("#periodMs").value;

        sendCommand(`flash/${numFlashes}/${periodMs}`);
    }
}

main();