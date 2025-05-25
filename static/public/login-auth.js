import { auth, provider } from "../firebase-config.js";

import { createUserWithEmailAndPassword,
         signInWithEmailAndPassword,
         signInWithPopup,
         sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";



/* == UI - Elements == */
const signInWithGoogleButtonEl = document.getElementById("sign-in-with-google-btn")
const signUpWithGoogleButtonEl = document.getElementById("sign-up-with-google-btn")
const emailInputEl = document.getElementById("email-input")
const passwordInputEl = document.getElementById("password-input")
const signInButtonEl = document.getElementById("sign-in-btn")
const createAccountButtonEl = document.getElementById("create-account-btn")
const emailForgotPasswordEl = document.getElementById("email-forgot-password")
const forgotPasswordButtonEl = document.getElementById("forgot-password-btn")

const errorMsgEmail = document.getElementById("email-error-message")
const errorMsgPassword = document.getElementById("password-error-message")
const errorMsgGoogleSignIn = document.getElementById("google-signin-error-message")



/* == UI - Event Listeners == */
if (signInWithGoogleButtonEl && signInButtonEl) {
    signInWithGoogleButtonEl.addEventListener("click", authSignInWithGoogle)
    signInButtonEl.addEventListener("click", authSignInWithEmail)
}

if (createAccountButtonEl) {
    createAccountButtonEl.addEventListener("click", authCreateAccountWithEmail)
}

if (signUpWithGoogleButtonEl) {
    signUpWithGoogleButtonEl.addEventListener("click", authSignUpWithGoogle)
}

if (forgotPasswordButtonEl) {
    forgotPasswordButtonEl.addEventListener("click", resetPassword)
}




/* === Main Code === */

/* = Functions - Firebase - Authentication = */

// Function to sign in with Google authentication
async function authSignInWithGoogle() {
    // Configure Google Auth provider with custom parameters
    provider.setCustomParameters({
        'prompt': 'select_account'
    });

    try {
        // Attempt to sign in with a popup and retrieve user data
        const result = await signInWithPopup(auth, provider);

        // Check if the result or user object is undefined or null
        if (!result || !result.user) {
            throw new Error('Authentication failed: No user data returned.');
        }

        const user = result.user;
        const email = user.email;

        // Ensure the email is available in the user data
        if (!email) {
            throw new Error('Authentication failed: No email address returned.');
        }

        // Retrieve ID token for the user
        const idToken = await user.getIdToken();
        
        // Log in the user using the obtained ID token
        loginUser(user, idToken);

    } catch (error) {
        // Handle errors by logging and potentially updating the UI
        handleLogging(error, 'Error during sign-in with Google');
    }
}



// Function to create new account with Google auth - will also sign in existing users
async function authSignUpWithGoogle() {
    provider.setCustomParameters({
        'prompt': 'select_account'
    });

    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        const email = user.email;

        // Sign in user
        const idToken = await user.getIdToken();
        loginUser(user, idToken);
     // 
    } catch (error) {
        // The AuthCredential type that was used or other errors.
        console.error("Error during Google signup: ", error.message);
        // Handle error appropriately here, e.g., updating UI to show an error message
    }
}




function authSignInWithEmail() {

    const email = emailInputEl.value
    const password = passwordInputEl.value

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            // Signed in 
            const user = userCredential.user;

            user.getIdToken().then(function(idToken) {
                loginUser(user, idToken)
            });

            console.log("User signed in: ", user)
        })
        .catch((error) => {
            const errorCode = error.code;
            console.error("Error code: ", errorCode)
            if (errorCode === "auth/invalid-email") {
                errorMsgEmail.textContent = "Invalid email"
            } else if (errorCode === "auth/invalid-credential") {
                errorMsgPassword.textContent = "Login failed - invalid email or password"
            } 
        });
}

async function addNewUserToFirestore(user) {
    const response = await fetch('/new_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            uid: user.uid,
            email: user.email,
            name: user.displayName || "" // u otro campo adicional
        })
    });

    if (!response.ok) {
        throw new Error("Fallo al registrar el usuario en Firestore/backend");
    }

    return await response.json(); // o simplemente return;
}

function showSignupSuccessModal() {
    console.log("✅ Ejecutando showSignupSuccessModal()");
    const modal = document.getElementById("modal-signup");
    modal.classList.remove("hidden");

    const okBtn = document.getElementById("modal-ok-btn");
    okBtn.addEventListener("click", () => {
        window.location.href = "/login";
    });
}

async function authCreateAccountWithEmail() {
    const email = emailInputEl.value;
    const password = passwordInputEl.value;

    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;

        await addNewUserToFirestore(user);
        const idToken = await user.getIdToken();

        // ✅ Muestra el modal
        showSignupSuccessModal();

    } catch (error) {
        const errorCode = error.code;

        if (errorCode === "auth/invalid-email") {
            errorMsgEmail.textContent = "Correo inválido";
        } else if (errorCode === "auth/weak-password") {
            errorMsgPassword.textContent = "Contraseña muy débil (mínimo 6 caracteres)";
        } else if (errorCode === "auth/email-already-in-use") {
            errorMsgEmail.textContent = "Ya existe una cuenta con este correo.";
        } else {
            console.error("Error al crear cuenta:", error.message);
        }
    }
}




function resetPassword() {
    const emailToReset = emailForgotPasswordEl.value

    clearInputField(emailForgotPasswordEl)

    sendPasswordResetEmail(auth, emailToReset)
    .then(() => {
        // Password reset email sent!
        const resetFormView = document.getElementById("reset-password-view")
        const resetSuccessView = document.getElementById("reset-password-confirmation-page")

        resetFormView.style.display = "none"
        resetSuccessView.style.display = "block"

    })
    .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
 
    });

}



function loginUser(user, idToken) {
    fetch('/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        // Guardar uid en sessionStorage para usarlo en el frontend
        sessionStorage.setItem("uid", data.uid);
        sessionStorage.setItem("user_role", data.role);
        sessionStorage.setItem("user_name", data.name);

        if (data.new_user) {
            window.location.href = '/register';
        } else {
            if(data.role == "admin") window.location.href = '/admin/';
            if (data.role === "professor") {
                window.location.href = '/professor/index';
            } else {
                window.location.href = '/student/';
            }
        }
    })
    .catch(error => {
        console.error('Error con la petición Fetch:', error);
    });
}





// /* = Functions - UI = */
function clearInputField(field) {
	field.value = ""
}

function clearAuthFields() {
	clearInputField(emailInputEl)
	clearInputField(passwordInputEl)
}


