from __future__ import annotations

from sc_client import ScAddr, ScTemplate, ScTemplateResult
from sc_client.constants.common import ADDRS, ALIASES, ClientCommand, RequestType
from sc_client.core.pipelines.template_search_pipeline import TemplateSearchPipeline
from sc_client.models import Response, ScTemplateParams


class TemplateGeneratePipeline(TemplateSearchPipeline):
    command_type = ClientCommand.GENERATE_TEMPLATE
    request_type = RequestType.GENERATE_TEMPLATE

    def __call__(self, template: ScTemplate | str | ScAddr, params: ScTemplateParams) -> ScTemplateResult:
        payload = self._create_payload(template, params)
        response = self._sc_connection.send_message(self.request_type, payload)
        self._process_errors(response, payload)
        data = self._response_process(response)
        return data

    def _response_process(self, response: Response) -> ScTemplateResult:
        result = None
        if response.status:
            response_payload = response.payload
            aliases = response_payload.get(ALIASES)
            addrs_list = response_payload.get(ADDRS)
            addrs = [ScAddr(addr) for addr in addrs_list]
            result = ScTemplateResult(addrs, aliases)
        return result
