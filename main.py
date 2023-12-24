from fastapi import FastAPI, Request
import pyrebase
import os
from dotenv import load_dotenv
from time import time
from inference import get_inference_result
import json
import re
from datetime import datetime

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
  return {"message": "Deepcare API is ready!"}

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
              "error": True,
              "message": str(e)
            }
  

@app.post("/login")
async def login(request: Request):
  body = await request.json()
  try:
    email = body['email']
    password = body['password']

    user = auth.sign_in_with_email_and_password(email, password)

    token = user['idToken']
    userId = user['localId']
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
                "token": token,
                "isLogin": True
              },
            }
  except Exception as e:
      #If there is any error, redirect back to login
      return  {
                "error": True,
                "message": str(e),
                "loginResult": None,
              }

@app.post("/inference")
async def inference(request: Request):
  body = await request.json()

  # get current timestamp for this request
  current_timestamp = get_current_timestamp()
  if 'timestamp' in body:
    try:
      current_timestamp = int(body['timestamp'])
    except:
      pass

  try:

    # get body payload
    admissionId = filter_string(str(body["admission_id"])).encode('ascii')
    token = body["token"] # jwtToken idToken
    modelInput = body["model_input"] # dictionary

    # validate token
    userInfo = auth.get_account_info(token)
    userId = userInfo['users'][0]['localId']

    # get name by token
    data = db.child("users").get()
    name = data.val()[userId]["name"]

    # store model input to the database
    db.child("admissions").child(admissionId).child(current_timestamp).child('model_input').set(modelInput)

    # get model input list
    model_input_list = []
    for key, value in db.child("admissions").child(admissionId).get().val().items():
      current_modelInput = value.get("model_input", {})
      current_modelInput['timestamp'] = key
      model_input_list.append(current_modelInput)

    # debug
    json.dumps(model_input_list)

    # do inference
    modelOutput = get_inference_result(model_input_list)

    # store model output to the database
    db.child("admissions").child(admissionId).child(current_timestamp).child('model_output').set(modelOutput)

    # get model output list
    model_output_list = []
    for key, value in db.child("admissions").child(admissionId).get().val().items():
      current_modelOutput = value.get("model_output", {})
      current_modelOutput['timestamp'] = key
      model_output_list.append(current_modelOutput)

    return {
      "admission_id": admissionId,
      "caregiver": name,
      "model_output":  model_output_list
    }
  except Exception as e:
    return  {
              "error": True,
              "message": str(e)
            }

@app.get("/inference")
async def get_inference_data():
  try:
    model_output_list = []
    tempAdmissionTable = db.child("admissions")
    for key, value in tempAdmissionTable.get().val().items():
      current_modelOutput = {}
      current_modelOutput['admission_id'] = key
      # nested_modelOutput = {}
      nested_ouput_list = []
      for keyNested, valueNested in value:
        nested_modelOutput = valueNested.get("model_output", {})
        nested_modelOutput['timestamp'] = datetime.utcfromtimestamp(int(keyNested))
        nested_ouput_list.append(nested_modelOutput)
      current_modelOutput['model_output'] = nested_ouput_list
      model_output_list.append(current_modelOutput)
    return model_output_list
  except Exception as e:
    return  {
              "error": True,
              "message": str(e)
            }

def get_current_timestamp() -> int:
  return int(time())

def filter_string(input_str):
  # Define the regular expression pattern
  pattern = re.compile('[A-Za-z0-9]+')
  
  # Use the pattern to find all matches in the input string
  matches = pattern.findall(input_str)
  
  # Combine the matches into a single string
  filtered_str = ''.join(matches)
  
  return filtered_str
