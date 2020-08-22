function sendMessage() {
  // get messages div
  var messages = document.getElementById("messages");

  // get new message
  var message = document.getElementById("message").value;

  // display new message on screen
  var newNode = document.createElement("P");
  newNode.innerText = message;

  messages.appendChild(newNode);
}
