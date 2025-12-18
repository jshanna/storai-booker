"""API routes for story templates."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from beanie import PydanticObjectId
from loguru import logger

from app.models.template import Template
from app.schemas.template import (
    TemplateResponse,
    TemplateListResponse,
    TemplateCategoriesResponse,
)

router = APIRouter()


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_age: Optional[int] = Query(None, ge=0, le=100, description="Minimum age filter"),
    max_age: Optional[int] = Query(None, ge=0, le=100, description="Maximum age filter"),
    search: Optional[str] = Query(None, min_length=1, description="Search in name/description"),
):
    """
    List available story templates.

    Templates are system-wide and do not require authentication.
    Supports filtering by category, age range, and text search.
    """
    try:
        # Build query - only active templates
        query = {"is_active": True}

        if category:
            query["category"] = category

        # Age range filtering: template must overlap with requested range
        if min_age is not None:
            query["age_range_max"] = {"$gte": min_age}
        if max_age is not None:
            query["age_range_min"] = {"$lte": max_age}

        # Get templates sorted by sort_order
        if search:
            # Use text search with explicit filter
            templates = await Template.find(
                {"$text": {"$search": search}, **query}
            ).sort("+sort_order").to_list()
        else:
            templates = await Template.find(query).sort("+sort_order").to_list()

        return TemplateListResponse(
            templates=[
                TemplateResponse(
                    id=str(t.id),
                    name=t.name,
                    description=t.description,
                    generation_inputs=t.generation_inputs,
                    age_range_min=t.age_range_min,
                    age_range_max=t.age_range_max,
                    category=t.category,
                    tags=t.tags,
                    icon=t.icon,
                    cover_image_url=t.cover_image_url,
                )
                for t in templates
            ],
            total=len(templates),
        )
    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}",
        )


@router.get("/categories", response_model=TemplateCategoriesResponse)
async def list_categories():
    """
    List all available template categories.

    Does not require authentication.
    """
    try:
        # Get distinct categories from active templates
        templates = await Template.find({"is_active": True}).to_list()
        categories = sorted(set(t.category for t in templates))

        return TemplateCategoriesResponse(categories=categories)
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list categories: {str(e)}",
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """
    Get a specific template by ID.

    Does not require authentication.
    """
    try:
        try:
            obj_id = PydanticObjectId(template_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid template ID format",
            )

        template = await Template.get(obj_id)
        if not template or not template.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found",
            )

        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            description=template.description,
            generation_inputs=template.generation_inputs,
            age_range_min=template.age_range_min,
            age_range_max=template.age_range_max,
            category=template.category,
            tags=template.tags,
            icon=template.icon,
            cover_image_url=template.cover_image_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}",
        )
