from typing import List
from dataclasses import dataclass

from jinja2 import Template


@dataclass
class ClassAttribute:
    name: str
    datatype: str
    default_value: str = ""
    description: str = ""


@dataclass
class Field:
    name: str
    datatype: str
    index: bool
    unique: bool
    primary_key: bool
    foreign_key: bool
    default_value: str
    creation_method: str
    model: str


@dataclass
class Model:
    name: str
    plural: str
    fields: List[Field]


def create_sqlalchemy_model_class(model: Model) -> str:
    # TODO handle uppers and lowers in model
    datatypes = {"int": "Integer", "str": "String", "bool": "Boolean"}
    attributes = []
    for field in model.fields:
        args = ""
        args += datatypes[field.datatype]
        if field.primary_key:
            args += ", primary_key=True"
        if field.unique and field.primary_key is False:
            args += ", unique=True"
        if field.index:
            args += ", index=True"
        if field.default_value:
            args += f", default={str(field.default_value)}"
        attributes.append((field.name, args))

    relationships = [("items", '"Item", back_populates="owner"')]

    jinja2_template_string = open("templates/model_class.html", 'r').read()
    template = Template(jinja2_template_string)
    text = template.render(name=model.name.title(),
                           plural=model.plural.lower(),
                           attributes=attributes,
                           relationships=relationships)
    return text


def create_models_page(model_classes: List[str]) -> str:
    sqlalchemy_imports = ("Boolean", "Column", "ForeignKey", "Integer", "String")
    sqlalchemy_orm_imports = ("relationship", )
    sqlalchemy_imports_text = ", ".join(sqlalchemy_imports)
    sqlalchemy_orm_imports_text = ", ".join(sqlalchemy_orm_imports)
    jinja2_template_string = open("templates/models.html", 'r').read()
    template = Template(jinja2_template_string)
    html_template_string = template.render(sqlalchemy_imports_text=sqlalchemy_imports_text,
                                           sqlalchemy_orm_imports_text=sqlalchemy_orm_imports_text,
                                           model_classes=model_classes)
    return html_template_string


def create_schemas_page() -> str:
    jinja2_template_string = open("templates/schemas.html", 'r').read()
    template = Template(jinja2_template_string)
    html_template_string = template.render()
    return html_template_string


def create_class_text(name: str, base: str = "", class_attributes: List[ClassAttribute] = None, inner_class: str = "") -> str:
    if not class_attributes:
        class_attributes = []

    jinja2_template_string = open("templates/class.html", 'r').read()
    template = Template(jinja2_template_string)
    if not class_attributes:
        empty_class = True
    else:
        empty_class = False
    indented_inner_class = []
    for i, line in enumerate(inner_class.split("\n")):
        if i != 0:
            if line != "":
                line = "    " + line
        indented_inner_class.append(line)
    
    text = template.render(name=name, base=base, class_attributes=class_attributes, empty_class=empty_class,
                           inner_class="\n".join(indented_inner_class))
    return text


def main():
    fields = [Field(name="id", datatype="int", index=True, unique=True, primary_key=True,
                    foreign_key=False, default_value="", creation_method="", model=""),
             Field(name="email", datatype="str", index=True, unique=True, primary_key=False,
                    foreign_key=False, default_value="", creation_method="", model=""),
             Field(name="hashed_password", datatype="str", index=False, unique=False, primary_key=False,
                    foreign_key=False, default_value="", creation_method="", model=""),
             Field(name="is_active", datatype="bool", index=False, unique=False, primary_key=False,
                    foreign_key=False, default_value=True, creation_method="", model="")]
    user_model = Model(name="user", plural="users", fields=fields)

    text = create_sqlalchemy_model_class(user_model)
    model_classes = [text]
    page = create_models_page(model_classes)
    with open("output/models.py", "w") as f:
        f.write(page)

    page = create_schemas_page()
    with open("output/schemas.py", "w") as f:
        f.write(page)
    return


if __name__ == "__main__":
    main()
