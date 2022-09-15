"""
This source file is part of an OSTIS project. For the latest info, see https://github.com/ostis-ai
Distributed under the MIT License
(See an accompanying file LICENSE or a copy at http://opensource.org/licenses/MIT)
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import StreamHandler


def _setup_default_logger():
    logger = logging.getLogger(LOGGER_NAME)
    sh = StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    sh.setFormatter(formatter)
    logger.addHandler(sh)


LOGGER_NAME = "py-sc-client"
_setup_default_logger()
