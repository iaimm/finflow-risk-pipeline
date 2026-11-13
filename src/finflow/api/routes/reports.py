from datetime import date

from fastapi import APIRouter

from finflow.api.auth_dependencies import AdminUserDep
from finflow.api.dependencies import TransactionServiceDep


router = APIRouter(
    prefix="/api/v1/reports",
    tags=["reports"],
)


@router.get("/daily")
def get_daily_report(
    _admin: AdminUserDep,
    service: TransactionServiceDep,
) -> dict:
    _, total = service.list_transactions(
        limit=1,
        offset=0,
    )

    return {
        "report_date": date.today().isoformat(),
        "total_transactions": total,
    }