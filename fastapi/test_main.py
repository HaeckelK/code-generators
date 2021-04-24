import pytest

from main import create_class_text, ClassAttribute


def test_create_class_text_class_attributes():
    class_attributes = [ClassAttribute(name="title", datatype="str"),
                        ClassAttribute(name="description", datatype="Optional[str]", default_value="None")]
    result = create_class_text(name="ItemBase", base="BaseModel", class_attributes=class_attributes)
    assert result == """class ItemBase(BaseModel):

    title: str
    description: Optional[str] = None"""


def test_create_class_text_pass():
    result = create_class_text(name="ItemCreate", base="ItemBase", class_attributes=[])
    assert result == """class ItemCreate(ItemBase):
    pass"""


def test_create_class_text_no_base():
    class_attributes = [ClassAttribute(name="orm_mode", datatype="bool", default_value="True")]
    result = create_class_text(name="Config", class_attributes=class_attributes)
    assert result == """class Config:

    orm_mode: bool = True"""


# def test_create_class_text_inner_class():
#     inner_class = create_class_text

#     result = create_class_text(name="Item", base="ItemBase", class_attributes=class_attributes)
#     assert result == """class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True"""
