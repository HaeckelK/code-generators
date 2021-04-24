from typing import List
from dataclasses import dataclass

from jinja2 import Template

from base import FunctionDetails, ClassAttribute, create_function_text, ClassDetails, create_class_text


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


class Model:
    def __init__(self, name: str, plural: str, fields: List[Field]):
        self.name = name
        self.plural = plural
        self.fields = fields
        self.base_attributes: List[ClassAttribute] = []
        self.create_attributes: List[ClassAttribute] = []
        self.read_attributes: List[ClassAttribute] = []
        return

    def extract_attributes_from_fields(self):
        for field in self.fields:
            if field.creation_method == "base":
                self.base_attributes.append(
                    ClassAttribute(name=field.name, datatype=field.datatype, default_value=field.default_value)
                )
            if field.creation_method == "create":
                self.create_attributes.append(
                    ClassAttribute(name=field.name, datatype=field.datatype, default_value=field.default_value)
                )
            if field.creation_method == "read":
                self.read_attributes.append(
                    ClassAttribute(name=field.name, datatype=field.datatype, default_value=field.default_value)
                )
        return


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

    jinja2_template_string = open("templates/model_class.html", "r").read()
    template = Template(jinja2_template_string)
    text = template.render(
        name=model.name.title(), plural=model.plural.lower(), attributes=attributes, relationships=relationships
    )
    return text


def create_models_page(model_classes: List[str]) -> str:
    sqlalchemy_imports = ("Boolean", "Column", "ForeignKey", "Integer", "String")
    sqlalchemy_orm_imports = ("relationship",)
    sqlalchemy_imports_text = ", ".join(sqlalchemy_imports)
    sqlalchemy_orm_imports_text = ", ".join(sqlalchemy_orm_imports)
    jinja2_template_string = open("templates/models.html", "r").read()
    template = Template(jinja2_template_string)
    html_template_string = template.render(
        sqlalchemy_imports_text=sqlalchemy_imports_text,
        sqlalchemy_orm_imports_text=sqlalchemy_orm_imports_text,
        model_classes=model_classes,
    )
    return html_template_string


def create_schemas_page() -> str:
    jinja2_template_string = open("templates/schemas.html", "r").read()
    template = Template(jinja2_template_string)
    html_template_string = template.render()
    return html_template_string


def main_old():
    fields = [
        Field(
            name="id",
            datatype="int",
            index=True,
            unique=True,
            primary_key=True,
            foreign_key=False,
            default_value="",
            creation_method="",
            model="",
        ),
        Field(
            name="email",
            datatype="str",
            index=True,
            unique=True,
            primary_key=False,
            foreign_key=False,
            default_value="",
            creation_method="",
            model="",
        ),
        Field(
            name="hashed_password",
            datatype="str",
            index=False,
            unique=False,
            primary_key=False,
            foreign_key=False,
            default_value="",
            creation_method="",
            model="",
        ),
        Field(
            name="is_active",
            datatype="bool",
            index=False,
            unique=False,
            primary_key=False,
            foreign_key=False,
            default_value=True,
            creation_method="",
            model="",
        ),
    ]
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


def generate_crud_functions_from_model(model: Model) -> List[FunctionDetails]:
    output = []
    # GET by unique field
    unique_fields = ("id", "email")
    for field in unique_fields:
        field_datatype = "int"
        name = "get_" + model.name.lower() + "_by_" + field
        search_term = model.name.lower() + "_" + field
        function = FunctionDetails(
            name=name,
            arguments=[
                ClassAttribute(name="db", datatype="Session"),
                ClassAttribute(name=search_term, datatype=field_datatype),
            ],
            return_value=f"db.query(models.{model.name.title()}).filter(models.{model.name.title()}.{field} == {search_term}).first()",
        )
        output.append(function)
    return output


def generate_schemas_classes_for_model(
    name: str,
    base_attributes: List[ClassAttribute],
    create_attributes: List[ClassAttribute],
    read_attributes: List[ClassAttribute],
) -> List[ClassDetails]:
    output = []
    orm_class = ClassDetails(
        name="Config", class_attributes=[ClassAttribute(name="orm_mode", datatype="bool", default_value="True")]
    )
    base_class = ClassDetails(name=name.title() + "Base", base="BaseModel", class_attributes=base_attributes)
    output.append(base_class)
    create_class = ClassDetails(name=name.title() + "Create", base=base_class.name, class_attributes=create_attributes)
    output.append(create_class)
    read_class = ClassDetails(
        name=name.title(), base=base_class.name, class_attributes=read_attributes, inner_class=orm_class
    )
    output.append(read_class)
    return output


def main():
    fields = [
        Field(
            name="id",
            datatype="int",
            index=True,
            unique=True,
            primary_key=True,
            foreign_key=False,
            default_value="",
            creation_method="read",
            model="",
        ),
        Field(
            name="email",
            datatype="str",
            index=True,
            unique=True,
            primary_key=False,
            foreign_key=False,
            default_value="",
            creation_method="base",
            model="",
        ),
        Field(
            name="hashed_password",
            datatype="str",
            index=False,
            unique=False,
            primary_key=False,
            foreign_key=False,
            default_value="",
            creation_method="",
            model="",
        ),
        Field(
            name="password",
            datatype="str",
            index=False,
            unique=False,
            primary_key=False,
            foreign_key=False,
            default_value="",
            creation_method="create",
            model="",
        ),
        Field(
            name="is_active",
            datatype="bool",
            index=False,
            unique=False,
            primary_key=False,
            foreign_key=False,
            default_value=True,
            creation_method="read",
            model="",
        ),
        Field(
            name="items",
            datatype="List[Item]",
            index=False,
            unique=False,
            primary_key=False,
            foreign_key=False,
            default_value="[]",
            creation_method="read",
            model="",
        ),
    ]
    user_model = Model(name="user", plural="users", fields=fields)
    user_model.extract_attributes_from_fields()

    item_model = Model(name="item", plural="items", fields=[])
    item_model.base_attributes = [
        ClassAttribute(name="title", datatype="str"),
        ClassAttribute(name="description", datatype="Optional[str]", default_value="None"),
    ]
    item_model.create_attributes = []
    item_model.read_attributes = [
        ClassAttribute(name="id", datatype="int"),
        ClassAttribute(name="owner_id", datatype="int"),
    ]

    models = (user_model, item_model)

    # Schemas
    for model in models:
        classes = generate_schemas_classes_for_model(
            name=model.name,
            base_attributes=model.base_attributes,
            create_attributes=model.create_attributes,
            read_attributes=model.read_attributes,
        )
        for item in classes:
            print(create_class_text(item))
            print("\n")

    return
    functions = generate_crud_functions_from_model(user_model)
    for function in functions:
        print(create_function_text(function))
        print("\n")
    return
    # Create CRUD file
    get_user = FunctionDetails(
        name="get_user",
        arguments=[ClassAttribute(name="db", datatype="Session"), ClassAttribute(name="user_id", datatype="int")],
        return_value="db.query(models.User).filter(models.User.id == user_id).first()",
    )

    get_user_by_email = FunctionDetails(
        name="get_user_by_email",
        arguments=[ClassAttribute(name="db", datatype="Session"), ClassAttribute(name="email", datatype="str")],
        return_value="db.query(models.User).filter(models.User.email == email).first()",
    )

    get_users = FunctionDetails(
        name="get_users",
        arguments=[
            ClassAttribute(name="db", datatype="Session"),
            ClassAttribute(name="skip", datatype="int", default_value="0"),
            ClassAttribute(name="limit", datatype="int", default_value="100"),
        ],
        return_value="db.query(models.User).offset(skip).limit(limit).all()",
    )

    create_user = FunctionDetails(
        name="create_user",
        arguments=[
            ClassAttribute(name="db", datatype="Session"),
            ClassAttribute(name="user", datatype="schemas.UserCreate"),
        ],
        return_value="db_user",
        body="""\
fake_hashed_password = user.password + "notreallyhashed"
db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
db.add(db_user)
db.commit()
db.refresh(db_user)""",
    )

    get_items = FunctionDetails(
        name="get_items",
        arguments=[
            ClassAttribute(name="db", datatype="Session"),
            ClassAttribute(name="skip", datatype="int", default_value="0"),
            ClassAttribute(name="limit", datatype="int", default_value="100"),
        ],
        return_value="db.query(models.Item).offset(skip).limit(limit).all()",
    )

    create_user_item = FunctionDetails(
        name="create_user_item",
        arguments=[
            ClassAttribute(name="db", datatype="Session"),
            ClassAttribute(name="item", datatype="schemas.ItemCreate"),
            ClassAttribute(name="user_id", datatype="int"),
        ],
        return_value="db_item",
        body="""\
db_item = models.Item(**item.dict(), owner_id=user_id)
db.add(db_item)
db.commit()
db.refresh(db_item)""",
    )

    return


if __name__ == "__main__":
    main()
