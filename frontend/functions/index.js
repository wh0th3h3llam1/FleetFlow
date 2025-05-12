/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const {onRequest} = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");

// Create and deploy your first functions
// https://firebase.google.com/docs/functions/get-started

// exports.helloWorld = onRequest((request, response) => {
//   logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });

const functions = require("firebase-functions");
const fetch = require("node-fetch");

exports.apiProxy = functions.https.onRequest(async (req, res) => {
  try {
    const apiRes = await fetch("http://your-api.com/data"); // Replace with your actual HTTP API
    const data = await apiRes.json();
    res.set('Access-Control-Allow-Origin', '*'); // Allow from frontend
    res.status(200).send(data);
  } catch (err) {
    res.status(500).send({ error: "Failed to fetch API" });
  }
});
