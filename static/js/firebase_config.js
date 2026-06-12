import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, OAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyDyQi7sdv_rgxIphejYZ6YtfX0Lp1Udkns",
  authDomain: "scrum-board-3b9fc.firebaseapp.com",
  projectId: "scrum-board-3b9fc",
  storageBucket: "scrum-board-3b9fc.firebasestorage.app",
  messagingSenderId: "579089488723",
  appId: "1:579089488723:web:9a2996d32e24feef781fa6",
  measurementId: "G-DS0W11J4XP"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

export const msProvider = new OAuthProvider('microsoft.com');
msProvider.setCustomParameters({
  // Force consent prompt
  prompt: 'consent'
});

async function submitTokenToBackend(token) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/manager/login';
    
    const tokenField = document.createElement('input');
    tokenField.type = 'hidden';
    tokenField.name = 'id_token';
    tokenField.value = token;
    form.appendChild(tokenField);

    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
        const csrfField = document.createElement('input');
        csrfField.type = 'hidden';
        csrfField.name = 'csrf_token';
        csrfField.value = csrfInput.value;
        form.appendChild(csrfField);
    }
    
    document.body.appendChild(form);
    form.submit();
}

export async function loginWithGoogle() {
    try {
        const result = await signInWithPopup(auth, googleProvider);
        const token = await result.user.getIdToken();
        await submitTokenToBackend(token);
    } catch (error) {
        console.error("Error signing in with Google", error);
        alert("Google Login failed: " + error.message + "\nMake sure you enabled Google Auth in the Firebase Console!");
    }
}

export async function loginWithMicrosoft() {
    try {
        const result = await signInWithPopup(auth, msProvider);
        const token = await result.user.getIdToken();
        await submitTokenToBackend(token);
    } catch (error) {
        console.error("Error signing in with Microsoft", error);
        alert("Microsoft Login failed: " + error.message + "\nMake sure you enabled Microsoft Auth in the Firebase Console!");
    }
}

// Make globally accessible
window.loginWithGoogle = loginWithGoogle;
window.loginWithMicrosoft = loginWithMicrosoft;
