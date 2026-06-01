"""
pb/routers package — thin HTTP layer.
Each router: auth → fetch → permission → service → return schema.
"""
from ninja import Router

from .projects import router as projects_router
from .boards import router as boards_router
from .columns import router as columns_router
from .invites import router as invites_router
from .members import router as members_router
from .tasks import router as tasks_router
from .comments import router as comments_router

router = Router()
router.add_router("", projects_router, tags=["Projects"])
router.add_router("", boards_router, tags=["Boards"])
router.add_router("", columns_router, tags=["Columns"])
router.add_router("", invites_router, tags=["Invites"])
router.add_router("", members_router, tags=["Members"])
router.add_router("", tasks_router, tags=["Tasks"])
router.add_router("", comments_router, tags=["Comments"])
