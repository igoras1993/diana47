import uuid
from datetime import datetime
from textwrap import dedent
from enum import Enum as BaseEnum

from sqlalchemy import Column, String, DateTime, Integer, BigInteger, ForeignKey, Boolean, Float, Unicode, UnicodeText, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash



class EnumeratorValue:
    def __init__(self, order_int, description=""):
        if type(order_int) is not int:
            raise AssertionError("order_int shoult be an integer.")

        if type(description) is not str:
            raise AssertionError("description should be a string.")
        self.order_int = order_int
        self.description = description

    def get_order(self):
        return self.order_int

    def get_description(self):
        return self.description

    def __hash__(self):
        return hash(self.order_int)

    def __eq__(self, other):
        return self.order_int == other


Base = declarative_base()


class BaseEntity(Base):
    __abstract__ = True
    created = Column(DateTime, default=datetime.utcnow)

    def descr(self):
        return "\n\tcreated=%r" % (self.created,)


class post(BaseEntity):
    __tablename__ = 'post'

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    author_id = Column(String(32), ForeignKey("users.id"))
    title = Column(UnicodeText, nullable=False)
    body = Column(UnicodeText, nullable=False)

    # Many (posts) to One (author)
    author = relationship("users", back_populates='posts')


# ##--AUTHENTICATION--##
class users(BaseEntity):
    __tablename__ = 'users'

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = Column(String(32), unique=True, nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    h_pass = Column(UnicodeText, nullable=False)
    confirmed = Column(Boolean, nullable=False, server_default='true')

    # One (user) to Many (posts)
    posts = relationship('post', back_populates='author')
    
    # connect user to rbac role
    user_roles = relationship("rbac_user_role", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, passwd):
        # set the heritage to tfg-internal user always when setting password
        self.h_pass = generate_password_hash(passwd)

    def set_password_via_hash(self, p_hash):
        # set the heritage to tfg-internal user always when setting password
        self.h_pass = p_hash

    def check_password(self, passwd):
        return self.h_pass is not None and check_password_hash(self.h_pass, passwd)

    def register_google_user(self, google_id, email=None):
        self.heritage = 'google'
        self.h_pass = None
        self.email = email
        self.id = google_id

    def check_integrity(self, id, email):
        return self.id == id and self.email == email and self.heritage == heritage

    def register_facebook_user(self, fb_id):
        self.heritage = 'facebook'
        self.h_pass = None
        self.email = None
        self.id = fb_id


# ##--RBAC--##
class ObjectEnum(BaseEnum):
    rbac_object = EnumeratorValue(1, dedent("""\
        List of all objects/resources that can be accessed via api and should be somehow protected by rbac
    """))

    rbac_action = EnumeratorValue(2, dedent("""\
        List of all actions that can be performed on rbac_objets. Cartesian product of objects and actions gives list 
        of all available permissions.
    """))

    rbac_permission = EnumeratorValue(3, dedent("""\
        Ths is assotiation table connecting Objects and Actions via M2M relationship. It represents cartesian product of
        objects and action. Pair (object, action) is called permisssion.
    """))

    rbac_role = EnumeratorValue(4, dedent("""\
        List of all currently defined roles, connected to permissions via Many-to-Many relationship, and to users also 
        by Many-to-Many relationship. 
    """))

    rbac_role_permission = EnumeratorValue(5, dedent("""\
        Association table that connects role with permissions by a M2M relationship.
    """))

    rbac_endpoints = EnumeratorValue(6, dedent("""\
        This table is reflection of all available endpoints on the api. This table is updated automatically every time
        when application starts. Actually no one should modify this table.  
    """))

    rbac_endpoint_permission = EnumeratorValue(7, dedent("""\
        This is assotiation table that connects endpoint and [required] permission by M2M relationship.
    """))

    rbac_user_role = EnumeratorValue(8, dedent("""\
        This is assotiation table that connects user with his role by M2M relationship.
    """))

    users = EnumeratorValue(9, dedent("""\
        This table contains info about registered users.
    """))

    blacklisted_tokens = EnumeratorValue(10, dedent("""\
        This table stores manually expired tokens. 
    """))


class ActionEnum(BaseEnum):

    insert = EnumeratorValue(1, dedent("""\
        Insert new value into object.
    """))

    read = EnumeratorValue(2, dedent("""\
        Read data from object.
    """))

    modify = EnumeratorValue(3, dedent("""\
        Modify requested object data state.
    """))

    delete = EnumeratorValue(4, dedent("""\
        Delete existing data in object.
    """))

    call = EnumeratorValue(5, dedent("""\
        Artificial action defined for stacking with artificial objects.
    """))


class rbac_object(BaseEntity):
    __tablename__ = 'rbac_object'

    # columns
    name = Column(UnicodeText, primary_key=True)
    description = Column(UnicodeText)

    # many 2 many
    permissions = relationship("rbac_permission", back_populates="object", cascade="all, delete-orphan")

    def __init__(self, obj_enum):
        if type(obj_enum) is not ObjectEnum:
            raise AssertionError("RBAC object constructor needs ObjectEnum on construction.")

        super().__init__(name=obj_enum.name,
                         description=obj_enum.value.get_description())


class rbac_action(BaseEntity):
    __tablename__ = 'rbac_action'

    # columns
    name = Column(UnicodeText, primary_key=True)
    description = Column(UnicodeText)

    # many 2 many
    permissions = relationship("rbac_permission", back_populates="action", cascade="all, delete-orphan")

    def __init__(self, act_enum):
        if type(act_enum) is not ActionEnum:
            raise AssertionError("RBAC action constructor needs ActionEnum on construction.")

        super().__init__(name=act_enum.name,
                         description=act_enum.value.get_description())


class rbac_permission(Base):
    __tablename__ = "rbac_permission"

    id = Column(String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)

    object_name = Column(String(32), ForeignKey("rbac_object.name"), primary_key=True)
    action_name = Column(String(32), ForeignKey("rbac_action.name"), primary_key=True)

    # this connects action with object
    object = relationship("rbac_object", back_populates="permissions")
    action = relationship("rbac_action", back_populates="permissions")

    # connecting role with permission
    role_permissions = relationship("rbac_role_permission", back_populates="permission", cascade="all, delete-orphan")

    # connecting endpoint with permission
    endpoint_permissions = relationship("rbac_endpoint_permission", back_populates="permission", cascade="all, delete-orphan")


class rbac_role(BaseEntity):
    __tablename__ = "rbac_role"

    # columns
    name = Column(UnicodeText, primary_key=True)
    description = Column(UnicodeText)

    # conecting role with permission
    role_permissions = relationship("rbac_role_permission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("rbac_user_role", back_populates="role", cascade="all, delete-orphan")


class rbac_role_permission(Base):
    __tablename__ = "rbac_role_permission"

    id = Column(String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)

    role_name = Column(String(32), ForeignKey("rbac_role.name"), primary_key=True)
    permission_id = Column(String(32), ForeignKey("rbac_permission.id"), primary_key=True)

    # conecting role with permisssion
    role = relationship("rbac_role", back_populates="role_permissions")
    permission = relationship("rbac_permission", back_populates="role_permissions")


class rbac_endpoint(Base):
    __tablename__ = "rbac_endpoint"

    name = Column(UnicodeText, primary_key=True)
    description = Column(UnicodeText)

    endpoint_permissions = relationship("rbac_endpoint_permission", back_populates="endpoint", cascade="all, delete-orphan")


class rbac_endpoint_permission(Base):
    __tablename__ = "rbac_endpoint_permission"

    id = Column(String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    endpoint_name = Column(String(32), ForeignKey("rbac_endpoint.name"), primary_key=True)
    permission_id = Column(String(32), ForeignKey("rbac_permission.id"), primary_key=True)

    # connecting endpoint with permission
    endpoint = relationship("rbac_endpoint", back_populates="endpoint_permissions")
    permission = relationship("rbac_permission", back_populates="endpoint_permissions")


class rbac_user_role(Base):
    __tablename__ = "rbac_user_role"

    id = Column(String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey("users.id"), primary_key=True)
    role_name = Column(String(32), ForeignKey("rbac_role.name"), primary_key=True)

    # connecting users with roles
    user = relationship("users", back_populates="user_roles")
    role = relationship("rbac_role", back_populates="user_roles")

