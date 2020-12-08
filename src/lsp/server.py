from pathlib import Path
from urllib.parse import urlparse

from pygls.features import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                            TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN, INITIALIZE)
from pygls.server import LanguageServer
from pygls.types import *

from pygls.protocol import LanguageServerProtocol
import logging

from src.bdd.Project import ProjectManager

logging.basicConfig(filename="ponthon.log", filemode="w", level=logging.DEBUG)


class PonthonProtocol(LanguageServerProtocol):
    """Override default LSP protocol (pygls) to link our reference server."""

    def bf_initialize(self, params: InitializeParams):
        """Called when the Language Server starts.
       Start Reference Server for given projects."""
        logging.info("Ponthon Language Server initialized.")

        # TODO : initialize Reference Server.
        rootPath = urlparse(params.rootUri).path

        logging.info(f"Workspace path is {rootPath}.")

        projectManager = ProjectManager()
        self.project = projectManager.lsp_add_workspace(rootPath)

        return super().bf_initialize(params)


class Ponthon(LanguageServer):
    """Our Language Server."""

    def __init__(self):
        super().__init__(protocol_cls=PonthonProtocol)

        self.project = None


ponthon = Ponthon()


@ponthon.feature(COMPLETION, trigger_characters=['.'])
def completions(ls, params: CompletionParams = None):
    """Returns completion items."""

    logging.info(ponthon.lsp.project.path)

    if params.context.triggerKind == CompletionTriggerKind.TriggerCharacter:
        no_point = Position(params.position.line, params.position.character - 1)

        word_before = ls.workspace.get_document(params.textDocument.uri).word_at_position(no_point)
        logging.info(f"Trigger character completion requested for {word_before}.")
        # TODO : Write dot completion.

        completions = []
    else:
        word_before = ls.workspace.get_document(params.textDocument.uri).word_at_position(params.position)

        logging.info(f"Completion requested for {word_before}")
        completions = ponthon.lsp.project.complete( word_before, urlparse(params.textDocument.uri).path)

        for completion in completions:
            logging.info(f"{completion} candidate was found.")
        # TODO : Write semantic competion.

    completionItems = [CompletionItem(x) for x in completions]

    return CompletionList(False, completionItems)

@ponthon.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    pass
    # documentPath = Path(urlparse(params.textDocument.uri).path)
    #
    # with open("test.test", "w") as file:
    #     text = ls.workspace.get_document(params.textDocument.uri)
    #     file.write(text.source)
    #
    # logging.info(f"Document {documentPath} did change.")