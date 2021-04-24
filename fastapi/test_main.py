import pytest

from main import create_class_text, ClassAttribute


def test_create_class_text():
    class_attributes = [ClassAttribute(name="title", datatype="str"),
                        ClassAttribute(name="description", datatype="Optional[str]", default_value="None")]
    result = create_class_text(name="ItemBase", base="BaseModel", class_attributes=class_attributes)
    assert result == """class ItemBase(BaseModel):

    title: str
    description: Optional[str] = None"""
