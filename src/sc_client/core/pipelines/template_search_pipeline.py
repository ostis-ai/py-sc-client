from __future__ import annotations

import re
from typing import get_origin

from sc_client import ScAddr, ScTemplate, ScTemplateResult, ScType, sc_exceptions
from sc_client.constants import common
from sc_client.constants.common import ADDRS, ALIASES, ClientCommand, RequestType
from sc_client.core.pipelines.processing_pipeline import ProcessingPipeline
from sc_client.models import Response, ScTemplateParams, ScTemplateValue
from sc_client.sc_exceptions import ErrorNotes


class TemplateSearchPipeline(ProcessingPipeline):
    command_type = ClientCommand.SEARCH_TEMPLATE
    request_type = RequestType.SEARCH_TEMPLATE

    def __call__(self, template: ScTemplate | str | ScAddr, params: ScTemplateParams) -> list[ScTemplateResult]:
        payload = self._create_payload(template, params)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    def _create_payload(
        self,
        template: ScTemplate | str | ScAddr,
        params: ScTemplateParams,
    ) -> any:
        if not isinstance(template, (ScTemplate, str, ScAddr)):
            raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScTemplate, str or ScArrd")
        if isinstance(template, ScAddr):
            payload_template = {
                common.TYPE: common.Types.ADDR,
                common.VALUE: template.value,
            }
        elif isinstance(template, str) and re.match("^([a-z]|\\d|_)+", template):
            payload_template = {common.TYPE: common.Types.IDTF, common.VALUE: template}
        elif isinstance(template, str):
            payload_template = template
        else:
            payload_template = self._process_template(template)

        payload_params = {}
        if params is not None:
            if not isinstance(params, get_origin(ScTemplateParams)):
                raise sc_exceptions.InvalidTypeError(ErrorNotes.EXPECTED_OBJECT_TYPES, "ScTemplateParams")
            for alias, addr in params.items():
                if isinstance(addr, ScAddr):
                    payload_params.update({alias: addr.value})
                else:
                    payload_params.update({alias: str(addr)})
        return {common.TEMPLATE: payload_template, common.PARAMS: payload_params}

    @classmethod
    def _process_template(cls, template: ScTemplate):
        payload_template = []
        for triple in template.triple_list:
            items = [triple.src, triple.edge, triple.trg]
            payload_template.append([cls._process_triple_item(item) for item in items])
        return payload_template

    @staticmethod
    def _process_triple_item(item: ScTemplateValue) -> dict:
        if isinstance(item.value, ScAddr):
            result = {common.TYPE: common.Types.ADDR, common.VALUE: item.value.value}
        elif isinstance(item.value, ScType):
            result = {common.TYPE: common.Types.TYPE, common.VALUE: item.value.value}
        else:
            result = {common.TYPE: common.Types.ALIAS, common.VALUE: item.value}
        if item.alias:
            result[common.ALIAS] = item.alias
        return result

    @staticmethod
    def _response_process(response: Response) -> list[ScTemplateResult]:
        result = []
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(ALIASES)
            all_addrs = response_payload.get(ADDRS)
            for addrs_list in all_addrs:
                addrs = [ScAddr(addr) for addr in addrs_list]
                result.append(ScTemplateResult(addrs, aliases))
        return result
