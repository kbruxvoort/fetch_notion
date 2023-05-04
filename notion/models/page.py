from __future__ import annotations

import datetime

from typing import TYPE_CHECKING, Optional, Any, Dict
from uuid import UUID


from pydantic import BaseModel, HttpUrl, Field

from fetchbim.utils import to_camel
from fetchbim import SharedRule
from .user import User
from .file_emoji import ExternalFile, HostedFile, EmojiObject
from .parent import PageParent, WorkspaceParent, DatabaseParent
from .property import (
    Property,
    RelationProperty,
    TitleProperty,
    CheckboxProperty,
    PersonProperty,
    EmailProperty,
    MultiSelectProperty,
    SelectProperty,
    PhoneProperty,
    URLProperty,
    FileProperty,
    DateProperty,
    NumberProperty,
    FormulaProperty,
    RelationProperty,
    RichTextProperty,
    RollupProperty,
    CreatedTimeProperty,
    CreatedByProperty,
    EditedTimeProperty,
    EditedByProperty,
    StatusProperty,
)


class Page(BaseModel):
    object: str = "page"
    id: UUID | str
    created_time: datetime.datetime | str
    created_by: User
    last_edited_time: datetime.datetime | str
    last_edited_by: User
    archived: bool = False
    icon: Optional[HostedFile | ExternalFile | EmojiObject] = None
    cover: Optional[HostedFile | ExternalFile] = None
    # properties: Dict[str, Property]
    properties: Dict[
        str,
        TitleProperty
        | CheckboxProperty
        | PersonProperty
        | EmailProperty
        | MultiSelectProperty
        | SelectProperty
        | PhoneProperty
        | URLProperty
        | FileProperty
        | DateProperty
        | NumberProperty
        | FormulaProperty
        | RelationProperty
        | RichTextProperty
        | RollupProperty
        | CreatedTimeProperty
        | CreatedByProperty
        | EditedTimeProperty
        | EditedByProperty
        | StatusProperty,
    ]
    parent: DatabaseParent | PageParent | WorkspaceParent
    url: HttpUrl

    @property
    def name(self):
        for _, prop in self.properties.items():
            if isinstance(prop, TitleProperty):
                return prop.get_value()

    class Config:
        arbitrary_types_allowed = True


class SharedAttributeProperties(BaseModel):
    shared_attribute_id: NumberProperty | None = None
    name: TitleProperty | None = None
    value: RichTextProperty | None = None
    attribute_type: FormulaProperty | None = None
    data_type: SelectProperty | None = None
    parameter_type: SelectProperty | None = None
    deleted: CheckboxProperty | None = None
    hidden: CheckboxProperty | None = None
    sort: NumberProperty | None = None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True


class SharedAttributePage(Page):
    properties: SharedAttributeProperties

    class Config:
        arbitrary_types_allowed = True


class SharedRuleProperties(BaseModel):
    shared_file_id: NumberProperty | None = None
    description: TitleProperty | None = None
    family_object_type: SelectProperty | None = None
    category_name: RichTextProperty | None = None
    parameter_name: RichTextProperty | None = None
    parameter_value: RichTextProperty | None = None
    match_type: SelectProperty | None = None
    parameter_value_match_type: FormulaProperty | None = None
    deleted: CheckboxProperty | None = None
    shared_attributes_relation: RelationProperty | None = None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True


class SharedRulePage(Page):
    properties: SharedRuleProperties
    shared_attributes: list[SharedAttributePage] = Field(default_factory=list)

    @property
    def name(self):
        if self.properties.description:
            return self.properties.description.get_value()

    def populate_shared_attributes(self, client):
        if self.properties.shared_attributes_relation.relation:
            for _id in self.properties.shared_attributes_relation.get_value():
                page_data = client.pages.retrieve(_id)
                shared_attribute = SharedAttributePage.parse_obj(page_data)
                self.shared_attributes.append(shared_attribute)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True

    def to_fetch(self):
        export_dict = self.dict(exclude={"match_type"}, by_alias=True)
        return SharedRule(id=self.properties.shared_file_id.get_value())
