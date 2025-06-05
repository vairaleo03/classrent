from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from ..database import get_database
from ..models.material import MaterialResponse, MaterialStats
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MaterialResponse])
async def get_all_materials(
    category: Optional[str] = Query(None, description="Filtra per categoria"),
    available_only: bool = Query(False, description="Solo materiali disponibili"),
    current_user: dict = Depends(get_current_user)
):
    """Recupera tutti i materiali disponibili"""
    db = await get_database()
    
    # Costruisci query di filtro
    filter_query = {}
    
    if category:
        filter_query["category"] = category
    
    if available_only:
        filter_query["is_available"] = True
    
    # Aggregazione per contare in quanti spazi è presente ogni materiale
    pipeline = [
        {"$match": filter_query},
        {
            "$lookup": {
                "from": "spaces",
                "localField": "name",
                "foreignField": "materials.name",
                "as": "spaces"
            }
        },
        {
            "$addFields": {
                "spaces_count": {"$size": "$spaces"}
            }
        },
        {"$project": {"spaces": 0}}
    ]
    
    materials = []
    async for material in db.materials.aggregate(pipeline):
        material_response = MaterialResponse(
            id=str(material["_id"]),
            spaces_count=material.get("spaces_count", 0),
            **{k: v for k, v in material.items() if k not in ["_id", "spaces_count"]}
        )
        materials.append(material_response)
    
    return materials

@router.get("/categories")
async def get_material_categories(current_user: dict = Depends(get_current_user)):
    """Recupera tutte le categorie di materiali"""
    db = await get_database()
    
    categories = await db.materials.distinct("category")
    return {"categories": categories}

@router.get("/stats", response_model=List[MaterialStats])
async def get_material_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Recupera statistiche di utilizzo dei materiali"""
    db = await get_database()
    
    # Aggregazione complessa per statistiche
    pipeline = [
        {
            "$lookup": {
                "from": "bookings",
                "localField": "name",
                "foreignField": "materials_requested",
                "as": "bookings"
            }
        },
        {
            "$lookup": {
                "from": "spaces",
                "localField": "name",
                "foreignField": "materials.name",
                "as": "spaces"
            }
        },
        {
            "$addFields": {
                "total_bookings": {"$size": "$bookings"},
                "most_used_space": {
                    "$arrayElemAt": ["$spaces.name", 0]
                },
                "last_usage_date": {
                    "$max": "$bookings.start_datetime"
                }
            }
        },
        {
            "$project": {
                "material_id": {"$toString": "$_id"},
                "material_name": "$name",
                "total_bookings": 1,
                "most_used_space": 1,
                "last_usage_date": 1,
                "average_usage_per_month": {
                    "$divide": ["$total_bookings", 12]  # Approssimazione
                }
            }
        }
    ]
    
    stats = []
    async for stat in db.materials.aggregate(pipeline):
        material_stat = MaterialStats(**stat)
        stats.append(material_stat)
    
    return sorted(stats, key=lambda x: x.total_bookings, reverse=True)

@router.get("/popular")
async def get_popular_materials(
    limit: int = Query(10, description="Numero di materiali da restituire"),
    current_user: dict = Depends(get_current_user)
):
    """Recupera i materiali più richiesti"""
    db = await get_database()
    
    # Aggregazione per trovare materiali più richiesti
    pipeline = [
        {"$unwind": "$materials_requested"},
        {"$group": {
            "_id": "$materials_requested",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {
            "material_name": "$_id",
            "request_count": "$count",
            "_id": 0
        }}
    ]
    
    popular_materials = []
    async for material in db.bookings.aggregate(pipeline):
        popular_materials.append(material)
    
    return popular_materials