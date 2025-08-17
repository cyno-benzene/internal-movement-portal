# Import the base from models
from app.models.base import Base

# Import all models here for Alembic
from app.models.employee import Employee
from app.models.job import Job, JobMatch
from app.models.application import Application
from app.models.approval import Approval
from app.models.notification import Notification
from app.models.invitation import Invitation, InvitationDecision