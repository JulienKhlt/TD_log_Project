from pygls.features import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                            TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN, INITIALIZE)
from pygls.server import LanguageServer
from pygls.types import *

from pygls.protocol import LanguageServerProtocol
import logging

logging.basicConfig(filename="ponthon.log", filemode="w", level=logging.DEBUG)


class PonthonProtocol(LanguageServerProtocol):
    """Override default LSP protocol (pygls) to link our reference server."""

    def bf_initialize(self, params: InitializeParams):
        """Called when the Language Server starts.
       Start Reference Server for given projects."""
        logging.info("Ponthon Language Server initialized.")

        # TODO : initialize Reference Server.

        return super().bf_initialize(params)


class Ponthon(LanguageServer):
    """Our LSP Server."""

    def __init__(self):
        super().__init__(protocol_cls=PonthonProtocol)


ponthon = Ponthon()


@ponthon.feature(COMPLETION, trigger_characters=['.'])
def completions(params: CompletionParams = None):
    """Returns completion items."""

    if params.context.triggerKind == CompletionTriggerKind.TriggerCharacter:
        logging.info("Trigger character completion requested.")
        # TODO : Write dot completion.
    else:
        logging.info("Completion requested")
        # TODO : Write semantic competion.
    return CompletionList(False, [
        CompletionItem('"'),
        CompletionItem('['),
        CompletionItem(']'),
        CompletionItem('{'),
        CompletionItem('}')
    ])
