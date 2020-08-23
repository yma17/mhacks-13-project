function sendMessage() {
  // // get messages div
  // var messages = document.getElementById("messages");

  // // get new message
  // var message = document.getElementById("message").value;

  // // display new message on screen
  // var newNode = document.createElement("P");
  // newNode.innerText = message;

  // messages.appendChild(newNode);

  // get messages container
  var messages = document.getElementById("messages");

  // get new message
  var message = document.getElementById("message").value;

  if (message) {
    // display new message on screen
    var newNode = document.createElement("TR");
    newNode.innerHTML = `<td class="text-right" style="border-style: none;"><span>${message} : </span><strong>You</strong><img class="rounded-circle mr-2" width="30" height="30" src="/static/assets/img/avatars/avatar4.jpeg"></td>`;

    messages.appendChild(newNode);
  }
}
