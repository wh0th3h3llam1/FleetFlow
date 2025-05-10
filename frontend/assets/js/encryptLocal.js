import { EncryptStorage } from "encrypt-storage";
let encryptLocal = null


function makeInstance(key) {
    if (key) {
        encryptLocal = EncryptStorage(key);
    }
}

export { makeInstance, encryptLocal }