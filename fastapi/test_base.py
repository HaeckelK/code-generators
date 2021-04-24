import pytest

from base import create_class_text, ClassAttribute, create_function_text, FunctionDetails


def test_create_class_text_class_attributes():
    class_attributes = [ClassAttribute(name="title", datatype="str"),
                        ClassAttribute(name="description", datatype="Optional[str]", default_value="None")]
    result = create_class_text(name="ItemBase", base="BaseModel", class_attributes=class_attributes)
    assert result == """\
class ItemBase(BaseModel):

    title: str
    description: Optional[str] = None"""


def test_create_class_text_pass():
    result = create_class_text(name="ItemCreate", base="ItemBase", class_attributes=[])
    assert result == """\
class ItemCreate(ItemBase):
    pass"""


def test_create_class_text_no_base():
    class_attributes = [ClassAttribute(name="orm_mode", datatype="bool", default_value="True")]
    result = create_class_text(name="Config", class_attributes=class_attributes)
    assert result == """\
class Config:

    orm_mode: bool = True"""


def test_create_class_text_inner_class():
    inner_class = create_class_text(name="Config", class_attributes=[ClassAttribute(name="orm_mode", datatype="bool", default_value="True")])

    class_attributes = [ClassAttribute(name="id", datatype="int"),
                        ClassAttribute(name="owner_id", datatype="int")] 
    result = create_class_text(name="Item", base="ItemBase", class_attributes=class_attributes, inner_class=inner_class)
    assert result == """\
class Item(ItemBase):

    id: int
    owner_id: int

    class Config:

        orm_mode: bool = True"""


def test_create_function_text():
    arguments = [ClassAttribute(name="db", datatype="Session"),
                 ClassAttribute(name="user_id", datatype="int")]
    return_value = "db.query(models.User).filter(models.User.id == user_id).first()"
    function_details = FunctionDetails(name="get_user", arguments=arguments, return_value=return_value)
    result = create_function_text(function_details=function_details)
    assert result == """\
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()"""
