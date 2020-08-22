// Your web app's Firebase configuration
var firebaseConfig = {
  apiKey: "AIzaSyAQk0A5csVTIUIEfvdXXiXaelEG3OWes9U",
  authDomain: "mhacks-13-project.firebaseapp.com",
  databaseURL: "https://mhacks-13-project.firebaseio.com",
  projectId: "mhacks-13-project",
  storageBucket: "mhacks-13-project.appspot.com",
  messagingSenderId: "999121062859",
  appId: "1:999121062859:web:c8e7a76b85aafa8eb2844e",
  measurementId: "G-PS38VSCWL3",
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);

var name = prompt("Enter your name");

function sendMessage() {
  // get message
  var message = document.getElementById("message").value;

  // save in database
  //   firebase
  //     .database()
  //     .ref("messages")
  //     .push()
  //     .set({ sender: name, message: message });
}
