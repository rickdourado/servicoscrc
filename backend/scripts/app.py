from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import backend.scripts.core_logic as core_logic
from pydantic import BaseModel

app = FastAPI(title="App Lúdico API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderData(BaseModel):
    items: List[core_logic.Level1Item]

@app.get("/api/data")
def get_data():
    items = core_logic.extract_data()
    return {"items": items}

@app.post("/api/save")
def save_data(data: OrderData):
    result = core_logic.save_new_order(data.items)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
