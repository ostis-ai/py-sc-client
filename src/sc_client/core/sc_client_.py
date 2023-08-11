from __future__ import annotations

import logging
from typing import Callable

from sc_client.core import pipelines
from sc_client.core.sc_connection import ScConnection
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScEvent,
    ScEventParams,
    ScIdtfResolveParams,
    ScLinkContent,
    SCsText,
    ScTemplate,
    ScTemplateParams,
    ScTemplateResult,
    ScType,
)
from sc_client.models.sc_construction import ScLinkContentData
from sc_client.sc_exceptions import ErrorNotes, InvalidTypeError


class ScClient:
    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._sc_connection = ScConnection()

        self.create_elements_pipeline = pipelines.CreateElementsPipeline(self._sc_connection)
        self.create_elements_by_scs_pipeline = pipelines.CreateElementsBySCsPipeline(self._sc_connection)
        self.check_elements_pipeline = pipelines.CheckElementsPipeline(self._sc_connection)
        self.delete_elements_pipeline = pipelines.DeleteElementsPipeline(self._sc_connection)
        self.resolve_keynodes_pipeline = pipelines.ResolveKeynodesPipeline(self._sc_connection)
        self.set_link_content_pipeline = pipelines.SetLinksContentPipeline(self._sc_connection)
        self.get_link_content_pipeline = pipelines.GetLinkContentPipeline(self._sc_connection)
        self.get_links_by_content_pipeline = pipelines.GetLinksByContentPipeline(self._sc_connection)
        self.get_links_by_content_substring_pipeline = pipelines.GetLinksByContentSubstringPipeline(self._sc_connection)
        self.get_links_contents_by_content_substring_pipeline = pipelines.GetLinksContentsByContentSubstringPipeline(
            self._sc_connection
        )
        self.template_search_pipeline = pipelines.TemplateSearchPipeline(self._sc_connection)
        self.template_generate_pipeline = pipelines.TemplateGeneratePipeline(self._sc_connection)
        self.events_create_pipeline = pipelines.EventsCreatePipeline(self._sc_connection)
        self.events_destroy_pipeline = pipelines.EventsDestroyPipeline(self._sc_connection)

    def connect(self, url: str) -> None:
        self._sc_connection.connect(url)

    def is_connected(self) -> bool:
        return self._sc_connection.is_connected()

    def disconnect(self) -> None:
        self._sc_connection.disconnect()

    def set_error_handler(self, callback) -> None:
        self._sc_connection.set_error_handler(callback)

    def set_reconnect_handler(
        self,
        reconnect_callback: Callable[[], None] = None,
        post_reconnect_callback: Callable[[], None] = None,
        reconnect_retries: int = None,
        reconnect_retry_delay: float = None,
    ) -> None:
        self._sc_connection.set_reconnect_handler(
            reconnect_callback,
            post_reconnect_callback,
            reconnect_retries,
            reconnect_retry_delay,
        )

    def check_elements(self, *addrs: ScAddr) -> list[ScType]:
        return self.check_elements_pipeline(*addrs)

    def create_elements(self, constr: ScConstruction) -> list[ScAddr]:
        return self.create_elements_pipeline(constr)

    def create_elements_by_scs(self, text: SCsText) -> list[bool]:
        return self.create_elements_by_scs_pipeline(text)

    def delete_elements(self, *addrs: ScAddr) -> bool:
        return self.delete_elements_pipeline(*addrs)

    def set_link_contents(self, *contents: ScLinkContent) -> bool:
        return self.set_link_content_pipeline(*contents)

    def get_link_content(self, *addr: ScAddr) -> list[ScLinkContent]:
        return self.get_link_content_pipeline(*addr)

    def get_links_by_content(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self.get_links_by_content_pipeline(*contents)

    def get_links_by_content_substring(self, *contents: ScLinkContent | ScLinkContentData) -> list[list[ScAddr]]:
        return self.get_links_by_content_substring_pipeline(*contents)

    def get_links_contents_by_content_substring(
        self, *contents: ScLinkContent | ScLinkContentData
    ) -> list[list[ScAddr]]:
        return self.get_links_contents_by_content_substring_pipeline(*contents)

    def resolve_keynodes(self, *params: ScIdtfResolveParams) -> list[ScAddr]:
        return self.resolve_keynodes_pipeline(*params)

    def template_search(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> list[ScTemplateResult]:
        return self.template_search_pipeline(template, params)

    def template_generate(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams = None,
    ) -> ScTemplateResult:
        return self.template_generate_pipeline(template, params)

    def events_create(self, *events: ScEventParams) -> list[ScEvent]:
        return self.events_create_pipeline(*events)

    def events_destroy(self, *events: ScEvent) -> bool:
        return self.events_destroy_pipeline(*events)

    def is_event_valid(self, event: ScEvent) -> bool:
        if not isinstance(event, ScEvent):
            raise InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScEvent")
        return bool(self._sc_connection.get_event(event.id))
