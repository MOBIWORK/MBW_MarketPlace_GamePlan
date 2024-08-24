importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js");

const firebaseConfig = {
  apiKey: "AIzaSyBpOODiGBUyfvXJ4sEh-eRermaqf0zb9EA",
  authDomain: "gameplan-fcm.firebaseapp.com",
  projectId: "gameplan-fcm",
  storageBucket: "gameplan-fcm.appspot.com",
  messagingSenderId: "593428166842",
  appId: "1:593428166842:web:37add159751bda3583aa83",
  measurementId: "G-G8XRKGYQ4G"
}

// Initialize the Firebase app in the service worker by passing the generated config

firebase.initializeApp(firebaseConfig);

// Retrieve firebase messaging
const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log("Received background message ", payload);

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});