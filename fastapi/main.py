from typing import Any, List
from dataclasses import dataclass

from jinja2 import Template


@dataclass
class Field:
    name: str
    datatype: str
    index: bool
    unique: bool
    primary_key: bool
    foreign_key: bool
    default_value: Any
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

    jinja2_template_string = open("templates/model_class.html", 'r').read()
    template = Template(jinja2_template_string)
    text = template.render(name=model.name.title(),
                           plural=model.plural.lower(),
                           attributes=attributes)
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
    return


if __name__ == "__main__":
    main()
