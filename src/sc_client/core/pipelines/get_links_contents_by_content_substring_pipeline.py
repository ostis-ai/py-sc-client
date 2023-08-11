from __future__ import annotations

from sc_client.constants import common
from sc_client.constants.common import ClientCommand, RequestType
from sc_client.core.pipelines.get_links_by_content_pipeline import GetLinksByContentPipeline


class GetLinksContentsByContentSubstringPipeline(GetLinksByContentPipeline):
    command_type = ClientCommand.CHECK_ELEMENTS
    request_type = RequestType.CHECK_ELEMENTS

    def _form_payload_content(self, content):
        return {
            common.COMMAND: common.CommandTypes.FIND_LINKS_CONTENTS_BY_CONTENT_SUBSTRING,
            common.DATA: content.data,
        }
