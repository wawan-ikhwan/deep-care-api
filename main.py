from fastapi import FastAPI, Request
import pyrebase
import os
from dotenv import load_dotenv
from inference import get_inference_result

load_dotenv()

app = FastAPI()

# Firebase initializer
firebaseConfig = {
  "apiKey": os.environ['FIREBASE_APIKEY'],
  "authDomain": "deep-care-capstone.firebaseapp.com",
  "databaseURL": "https://deep-care-capstone-default-rtdb.asia-southeast1.firebasedatabase.app",
  "storageBucket": "deep-care-capstone.appspot.com"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.post("/register") #Only listen to POST
async def register(request: Request):
  body = await request.json()       #Get the data submitted
  try:
    email = body["email"]
    password = body["password"]
    name = body["name"]

    #Try creating the user account using the provided data
    auth.create_user_with_email_and_password(email, password)
    #Login the user
    user = auth.sign_in_with_email_and_password(email, password)

    #Append data to the firebase realtime database
    data = {"name": name, "email": email}
    db.child("users").child(user["localId"]).set(data)
    #Go to welcome page
    return  {
              "error": False,
              "message": "successfully stored in database!"
            }
  except Exception as e:
    #If there is any error, redirect to register
    return {
              "error": False,
              "message": str(e)
            }
  

@app.post("/login")
async def login(request: Request):
  body = await request.json()
  try:
    email = body["email"]
    password = body["password"]

    user = auth.sign_in_with_email_and_password(email, password)

    token = user['idToken']
    userId = user["localId"]
    #Get the name of the user
    data = db.child("users").get()
    name = data.val()[userId]["name"]
    #Redirect to welcome page
    return  {
              "error": False,
              "message": "success",
              "loginResult": {
                "name": name,
                "userId": userId,
                "token": token
              }
            }
  except Exception as e:
      #If there is any error, redirect back to login
      return  {
                "error": False,
                "message": str(e),
                "loginResult": None
              }

@app.post("/inference")
async def inference(request: Request):
  body = await request.json()
  try:
    admissionId = body["admission_id"]
    token = body["token"] # jwtToken
    modelInput = body["model_input"] # dictionary
    userInfo = auth.get_account_info(token)
    userId = userInfo['users'][0]['localId']

    data = db.child("users").get()
    name = data.val()[userId]["name"]

    modelOutput = get_inference_result(modelInput)

    return {
      "admission_id": admissionId,
      "caregiver": name,
      "model_output": modelOutput
    }
  except Exception as e:
    return  {
              "error": False,
              "message": str(e)
            }