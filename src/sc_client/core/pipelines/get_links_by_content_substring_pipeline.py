from __future__ import annotations

from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.get_links_contents_by_content_substring_pipeline import GetLinksByContentPipeline


class GetLinksByContentSubstringPipeline(GetLinksByContentPipeline):
    command_type = ClientCommand.GET_LINKS_BY_CONTENT_SUBSTRING
    request_type = RequestType.CONTENT

    def _form_payload_content(self, content) -> any:
        return {
            common.COMMAND: common.CommandTypes.FIND_LINKS_BY_SUBSTRING,
            common.DATA: content.data,
        }
