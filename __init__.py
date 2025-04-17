from aiogram import Router
from .admin import admin_router
from .puzzles import puzzles_router
from .rating import rating_router

router = Router()
router.include_router(admin_router)
router.include_router(puzzles_router)
router.include_router(rating_router)

__all__ = ['router']
