from typing import List
from dataclasses import dataclass

from jinja2 import Template


@dataclass
class ClassAttribute:
    name: str
    datatype: str
    default_value: str = ""
    description: str = ""


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
