from fastapi import FastAPI, UploadFile, File
import uvicorn
import uuid
from extraction import *
import os
app = FastAPI()

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{(str(uuid.uuid1())+'.pdf')}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    result=extract_key_values(file_location)
    os.remove(file_location)
    return {"filename": result}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


