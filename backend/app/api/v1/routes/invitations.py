from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
import logging
from app.db.session import get_db
from app.models.employee import Employee
from app.models.job import Job
from app.models.invitation import Invitation, InvitationDecision
from app.schemas.invitation import (
    InvitationCreate, InvitationResponse, InvitationDetailResponse,
    InvitationDecisionCreate, InvitationDecisionResponse
)
from app.api.v1.deps import get_current_user, require_manager_or_hr_or_admin, require_hr_or_admin

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=List[InvitationDetailResponse])
async def get_my_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get invitations for the current employee"""
    logger.info(f"Getting invitations for employee {current_user.employee_id}")
    
    result = await db.execute(
        select(Invitation)
        .options(
            selectinload(Invitation.job).selectinload(Job.manager),
            selectinload(Invitation.inviter)
        )
        .where(Invitation.employee_id == current_user.id)
        .order_by(Invitation.created_at.desc())
    )
    invitations = result.scalars().all()
    
    return [
        InvitationDetailResponse(
            id=str(invitation.id),
            job={
                "id": str(invitation.job.id),
                "title": invitation.job.title,
                "team": invitation.job.team,
                "note": invitation.job.note,
                "manager_name": invitation.job.manager.name
            },
            employee={
                "id": str(invitation.employee_id),
                "name": current_user.name,
                "email": current_user.email
            },
            inviter={
                "id": str(invitation.inviter.id),
                "name": invitation.inviter.name,
                "email": invitation.inviter.email,
                "role": invitation.inviter.role
            },
            channel=invitation.channel,
            content=invitation.content,
            status=invitation.status,
            manager_notes=invitation.manager_notes,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at
        )
        for invitation in invitations
    ]

@router.post("/{invitation_id}/respond", response_model=InvitationDecisionResponse)
async def respond_to_invitation(
    invitation_id: UUID,
    decision_data: InvitationDecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Respond to an invitation (accept/decline/request_info)"""
    logger.info(f"Employee {current_user.employee_id} responding to invitation {invitation_id}")
    
    # Get invitation and verify it belongs to current user
    result = await db.execute(
        select(Invitation).where(
            Invitation.id == invitation_id,
            Invitation.employee_id == current_user.id
        )
    )
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or not accessible"
        )
    
    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has already been responded to"
        )
    
    # Validate decision
    if decision_data.decision not in ["accept", "decline", "request_info"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid decision. Must be accept, decline, or request_info"
        )
    
    # Create decision record
    decision = InvitationDecision(
        invitation_id=invitation.id,
        actor_id=current_user.id,
        decision=decision_data.decision,
        note=decision_data.note
    )
    
    # Update invitation status
    if decision_data.decision == "accept":
        invitation.status = "accepted"
    elif decision_data.decision == "decline":
        invitation.status = "declined"
    else:  # request_info
        invitation.status = "info_requested"
    
    db.add(decision)
    await db.commit()
    await db.refresh(decision)
    
    logger.info(f"Invitation {invitation_id} responded with {decision_data.decision}")
    
    return InvitationDecisionResponse(
        id=str(decision.id),
        invitation_id=str(decision.invitation_id),
        actor_id=str(decision.actor_id),
        decision=decision.decision,
        note=decision.note,
        created_at=decision.created_at
    )

@router.post("/", response_model=List[InvitationResponse])
async def create_invitations(
    invitation_data: InvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_hr_or_admin())
):
    """Create invitations for employees to a job (HR only)"""
    logger.info(f"HR user {current_user.employee_id} creating invitations for job {invitation_data.job_id}")
    
    # Verify job exists
    result = await db.execute(select(Job).where(Job.id == invitation_data.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Create invitations
    invitations = []
    for employee_id in invitation_data.employee_ids:
        # Check if employee exists
        emp_result = await db.execute(select(Employee).where(Employee.id == employee_id))
        employee = emp_result.scalar_one_or_none()
        
        if not employee:
            logger.warning(f"Employee {employee_id} not found, skipping invitation")
            continue
        
        # Check if invitation already exists
        existing_result = await db.execute(
            select(Invitation).where(
                Invitation.job_id == invitation_data.job_id,
                Invitation.employee_id == employee_id
            )
        )
        if existing_result.scalar_one_or_none():
            logger.warning(f"Invitation already exists for employee {employee_id}, skipping")
            continue
        
        # Create invitation
        invitation = Invitation(
            job_id=job.id,
            employee_id=employee.id,
            inviter_id=current_user.id,
            content=invitation_data.content or f"You're invited to consider the {job.title} position on the {job.team} team.",
            manager_notes=invitation_data.manager_notes,
            status="pending"
        )
        
        db.add(invitation)
        invitations.append(invitation)
    
    await db.commit()
    
    # Refresh to get IDs
    for invitation in invitations:
        await db.refresh(invitation)
    
    logger.info(f"Created {len(invitations)} invitations for job {invitation_data.job_id}")
    
    return [
        InvitationResponse(
            id=str(invitation.id),
            job_id=str(invitation.job_id),
            employee_id=str(invitation.employee_id),
            inviter_id=str(invitation.inviter_id),
            channel=invitation.channel,
            content=invitation.content,
            status=invitation.status,
            manager_notes=invitation.manager_notes,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at
        )
        for invitation in invitations
    ]

@router.get("/sent", response_model=List[InvitationDetailResponse])
async def get_sent_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_hr_or_admin())
):
    """Get invitations sent by HR"""
    logger.info(f"Getting sent invitations for HR user {current_user.employee_id}")
    
    result = await db.execute(
        select(Invitation)
        .options(
            selectinload(Invitation.job),
            selectinload(Invitation.employee),
            selectinload(Invitation.inviter)
        )
        .where(Invitation.inviter_id == current_user.id)
        .order_by(Invitation.created_at.desc())
    )
    invitations = result.scalars().all()
    
    return [
        InvitationDetailResponse(
            id=str(invitation.id),
            job={
                "id": str(invitation.job.id),
                "title": invitation.job.title,
                "team": invitation.job.team,
                "note": invitation.job.note,
                "manager_name": invitation.job.manager.name if invitation.job.manager else "Unknown"
            },
            employee={
                "id": str(invitation.employee.id),
                "employee_id": invitation.employee.employee_id,
                "name": invitation.employee.name,
                "email": invitation.employee.email
            },
            inviter={
                "id": str(invitation.inviter.id),
                "employee_id": invitation.inviter.employee_id,
                "name": invitation.inviter.name,
                "email": invitation.inviter.email
            },
            channel=invitation.channel,
            content=invitation.content,
            status=invitation.status,
            manager_notes=invitation.manager_notes,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at
        )
        for invitation in invitations
    ]
