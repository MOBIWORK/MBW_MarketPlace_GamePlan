import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';
import { firebaseConfig, vapid_key} from './config_firebase'

export async function initMessageFireBase(){
    let urlConfigApp = "/api/method/gameplan.api.get_config_app_firebase";
    const responseConfigApp = await fetch(urlConfigApp);
    const objResponse = await responseConfigApp.json();
    let objConfigApp = objResponse['message'] != null ? objResponse['message'] : firebaseConfig();
    let urlVapidKey = "/api/method/gameplan.api.get_vapid_key_firebase";
    const responseVapidKey = await fetch(urlVapidKey);
    const objResponseVapidKey = await responseVapidKey.json();
    let vapidKey = objResponseVapidKey['message'] != null? objResponseVapidKey['message'] : vapid_key();
    initializeApp(objConfigApp);

    if('serviceWorker' in navigator){
        const messaging = getMessaging();
        let urlExistToken = "/api/method/gameplan.api.is_exist_token";
        let responseExistToken = await fetch(urlExistToken);
        let objExistToken = await responseExistToken.json();
        let isExistToken = objExistToken['message'];
        Notification.requestPermission().then((permission) => {
            if (permission === 'granted'){
                if(isExistToken == 0){
                    getToken(messaging, { vapidKey: vapidKey}).then((currentToken) => {
                        if(currentToken){
                            const myHeaders = new Headers();
                            myHeaders.append("Content-Type", "application/json");
                            fetch("/api/method/gameplan.api.token_firebase", {
                                method: "POST",
                                body: JSON.stringify({ token: currentToken }),
                                headers: myHeaders
                            })
                        }
                    })
                }
            }
        });
        onMessage(messaging, (payload) => {
            var title = payload.data.title;
            var options = {
                body: payload.data.body,
                icon: payload.data.icon,
                image: payload.data.image
            }
            var myNotification = new Notification(title, options)
        })
    }
}