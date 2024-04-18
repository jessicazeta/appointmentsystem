from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from fastapi.staticfiles import StaticFiles
from bson import ObjectId

client = MongoClient("mongodb+srv://AppSysDB:admin12345@cluster0.mxljdzx.mongodb.net/")
db = client["appointmentsystem"]
collection = db["appointments"]
confirmed_appointments_collection = db["confirmed_appointments"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")
#CSS Setup
app.mount("/static",StaticFiles(directory="static", html=True),name="static") 

#home page route
@app.get("/", response_class=HTMLResponse)
async def display_homepage(request: Request):
    return templates.TemplateResponse("home-page.html", {"request": request})

#counselor page route
@app.get("/counselor-page", response_class=HTMLResponse)
async def list_data(request: Request):
    db_appointments = list(collection.find({})) # Fetch all documents
    return templates.TemplateResponse("counselor-page.html", {"request": request, "data": db_appointments})

#route to view a single appointment
@app.get("/view-appointment/{appointment_id}", response_class=HTMLResponse)
async def display_appointment(request: Request, appointment_id: str):
    appointment = collection.find_one({"_id": ObjectId(appointment_id)})
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return templates.TemplateResponse("view-appointment.html", {"request": request, "appointment": appointment})

# Confirm appointment
@app.post("/confirm-appointment/{appointment_id}")
async def confirm_appointment(appointment_id: str):
    # Retrieve the appointment from the original collection
    appointment = collection.find_one({"_id": ObjectId(appointment_id)})
    if appointment:
        # Move the appointment to the confirmed appointments collection
        confirmed_appointments_collection.insert_one(appointment)
        # Optionally, you can remove the appointment from the original collection
        collection.delete_one({"_id": ObjectId(appointment_id)})
        return {"message": "Appointment confirmed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
#Display create-appointment page
@app.get("/create-appointment", response_class=HTMLResponse)
async def display_create_appointment(request: Request):
    return templates.TemplateResponse("create-appointment.html", {"request": request})

#function to add the appointment to MongoDB
@app.post("/add", response_class=HTMLResponse)
async def add_data(request: Request):
    form_data = await request.form()

    date = form_data.get("date")
    time = form_data.get("time")
    name = form_data.get("name")
    email = form_data.get("email")
    
    if not date or not time or not name or not email:
        raise HTTPException(status_code=400, detail="Date, time, name, and email are required fields")

    inserted_data = collection.insert_one({"date": date, "time": time, "name": name, "email": email})
    
    if inserted_data.inserted_id:
        # Redirect to a different page or display a success message
        return "Appointment Created Succesfully"
    else:
        # Handle the error appropriately
        raise HTTPException(status_code=500, detail="Failed to insert data into MongoDB")

    
