import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyA0tLHWda0r6csMVlcqwk-rKTS-d5IvAM4",
  authDomain: "flask-website-e78b1.firebaseapp.com",
  projectId: "flask-website-e78b1",
  storageBucket: "flask-website-e78b1.firebasestorage.app",
  messagingSenderId: "566717830616",
  appId: "1:566717830616:web:feea4980bb32f24b2acead",
  measurementId: "G-1EFGDRXMWL"
};

  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };