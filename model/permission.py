# policy_engine.py
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from beanie import Document
from model.user import User
import datetime


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


class ResourceType(str, Enum):
    DOCUMENT = "document"
    USER = "user"
    PROJECT = "project"
    SYSTEM = "system"


class PolicyCondition(BaseModel):
    field: str
    operator: str  # "eq", "ne", "gt", "lt", "in", "contains", etc.
    value: Any


class PolicyRule(BaseModel):
    resource_type: ResourceType
    resource_id: Optional[str] = None  # None means all resources of this type
    permissions: List[Permission]
    conditions: Optional[List[PolicyCondition]] = None


class Policy(Document):
    name: str
    description: Optional[str] = None
    rules: List[PolicyRule]
    users: List[str] = []  # List of user IDs or usernames
    groups: List[str] = []  # List of group names
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "policies"
        use_state_management = True

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()


class AccessRequest(BaseModel):
    user: User
    resource_type: ResourceType
    resource_id: Optional[str] = None
    permission: Permission
    context: Optional[Dict[str, Any]] = None


class PolicyEngine:
    def __init__(self):
        self.operators = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "in": lambda a, b: a in b,
            "contains": lambda a, b: b in a if hasattr(a, "__contains__") else False,
            "startswith": lambda a, b: (
                a.startswith(b) if hasattr(a, "startswith") else False
            ),
            "endswith": lambda a, b: a.endswith(b) if hasattr(a, "endswith") else False,
        }

    async def evaluate_condition(
        self, condition: PolicyCondition, context: Dict[str, Any]
    ) -> bool:
        """Evaluate a single condition against the context"""
        field_value = context.get(condition.field)
        operator_func = self.operators.get(condition.operator)

        if operator_func is None:
            raise ValueError(f"Unknown operator: {condition.operator}")

        return operator_func(field_value, condition.value)

    async def evaluate_conditions(
        self, conditions: List[PolicyCondition], context: Dict[str, Any]
    ) -> bool:
        """Evaluate all conditions (AND logic)"""
        if not conditions:
            return True

        for condition in conditions:
            if not await self.evaluate_condition(condition, context):
                return False
        return True

    async def evaluate_rule(self, rule: PolicyRule, request: AccessRequest) -> bool:
        """Evaluate if a rule applies to the access request"""
        # Check resource type match
        if rule.resource_type != request.resource_type:
            return False

        # Check resource ID match (if specified in rule)
        if rule.resource_id and rule.resource_id != request.resource_id:
            return False

        # Check permission match
        if request.permission not in rule.permissions:
            return False

        # Evaluate conditions
        context = request.context or {}
        context.update(
            {
                "user_id": request.user.id,
                "username": request.user.username,
                "resource_type": request.resource_type,
                "resource_id": request.resource_id,
                "permission": request.permission,
            }
        )

        return await self.evaluate_conditions(rule.conditions, context)

    async def has_access(
        self,
        user: User,
        resource_type: ResourceType,
        permission: Permission,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Check if user has access to a resource"""
        # Superusers have all access
        if user.is_superuser:
            return True

        # Get all active policies for this user
        policies = await Policy.find(
            Policy.is_active == True,
            Policy.users.contains(user.username)
            | Policy.users.contains(str(user.id))
            | Policy.groups.any(),  # You might want to implement group membership check
        ).to_list()

        request = AccessRequest(
            user=user,
            resource_type=resource_type,
            resource_id=resource_id,
            permission=permission,
            context=context,
        )

        # Check each policy
        for policy in policies:
            for rule in policy.rules:
                if await self.evaluate_rule(rule, request):
                    return True

        return False

    async def get_user_permissions(
        self, user: User, resource_type: ResourceType, resource_id: Optional[str] = None
    ) -> List[Permission]:
        """Get all permissions a user has for a resource"""
        if user.is_superuser:
            return list(Permission)

        permissions = set()
        policies = await Policy.find(
            Policy.is_active == True,
            Policy.users.contains(user.username) | Policy.users.contains(str(user.id)),
        ).to_list()

        for policy in policies:
            for rule in policy.rules:
                if rule.resource_type == resource_type:
                    if rule.resource_id is None or rule.resource_id == resource_id:
                        context = {"user_id": user.id, "username": user.username}
                        if await self.evaluate_conditions(rule.conditions, context):
                            permissions.update(rule.permissions)

        return list(permissions)
