from __future__ import annotations
from typing import List
from dataclasses import dataclass

from jinja2 import Template


# TODO rename to Argument
@dataclass
class ClassAttribute:
    name: str
    datatype: str
    default_value: str = ""
    description: str = ""


@dataclass
class FunctionDetails:
    name: str
    arguments: List[ClassAttribute]
    return_value: str
    body: str = ""
    decorator: str = ""


@dataclass
class ClassDetails:
    name: str
    base: str = ""
    class_attributes: List[ClassAttribute] = None
    inner_class: ClassDetails = None


def create_class_text(class_details: ClassDetails) -> str:
    if not class_details.class_attributes:
        class_details.class_attributes = []

    jinja2_template_string = open("templates/class.html", 'r').read()
    template = Template(jinja2_template_string)
    if not class_details.class_attributes:
        empty_class = True
    else:
        empty_class = False
    indented_inner_class = []
    if class_details.inner_class:
        inner_class_text = create_class_text(class_details.inner_class)
        for i, line in enumerate(inner_class_text.split("\n")):
            if i != 0:
                if line != "":
                    line = "    " + line
            indented_inner_class.append(line)
    
    text = template.render(name=class_details.name, base=class_details.base, class_attributes=class_details.class_attributes,
                           empty_class=empty_class, inner_class="\n".join(indented_inner_class))
    return text


def create_function_text(function_details: FunctionDetails) -> str:
    jinja2_template_string = open("templates/function.html", 'r').read()
    template = Template(jinja2_template_string)
    
    arguments_texts = []
    for argument in function_details.arguments:
        text = argument.name + ": " + argument.datatype
        if argument.default_value != "":
            text += " = " + argument.default_value
        arguments_texts.append(text)

    arguments_text = ", ".join(arguments_texts)

    if function_details.body != "":
        indented_text_lines = []
        for line in function_details.body.split("\n"):
            indented_text_lines.append("    " + line)
        body = "\n".join(indented_text_lines)
    else:
        body = ""

    text = template.render(function_details=function_details, arguments_text=arguments_text, body=body,
                           decorator=function_details.decorator)
    return text
