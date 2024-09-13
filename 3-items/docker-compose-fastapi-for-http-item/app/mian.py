from fastapi import FastAPI, HTTPException
from collections import defaultdict
import uvicorn


app = FastAPI()

# Predefined item counts initialized to zero
predefined_counts = {
    "apple": 0,
    "kiwi": 0,
    "papaya": 0
}

# Dictionary to hold counts of items
item_counts = defaultdict(int)


@app.get("/items")
async def get_items_count():
    """Get the count of all items including predefined counts."""
    all_counts = {**predefined_counts, **dict(item_counts)}
    return {"items": all_counts}


@app.post("/items/{item_name}")
async def create_item(item_name: str):
    """Create an item and initialize its count."""
    item_counts[item_name] += 1
    return {"message": f"Item '{item_name}' created.", "count": item_counts[item_name]}



@app.delete("/items/{item_name}")
async def delete_item(item_name: str):
    """Delete an item, reducing its count."""
    if item_counts[item_name] > 0:
        item_counts[item_name] -= 1
        return {"message": f"Item '{item_name}' deleted.", "count": item_counts[item_name]}
    else:
        raise HTTPException(status_code=404, detail="Item not found or count is zero.")
