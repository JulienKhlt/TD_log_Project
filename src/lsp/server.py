import logging
from pathlib import Path
from urllib.parse import urlparse

from pygls.features import (COMPLETION, INITIALIZE, TEXT_DOCUMENT_DID_CHANGE,
                            TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN)
from pygls.protocol import LanguageServerProtocol
from pygls.server import LanguageServer
from pygls.types import (CompletionItem, CompletionItemKind, CompletionList,
                         CompletionParams, CompletionTriggerKind,
                         DidChangeTextDocumentParams, InitializeParams,
                         Position)
from src.bdd.Project import ProjectManager
from src.lsp.CompletionParser import CompletionParser

logging.basicConfig(filename="ponthon.log", filemode="w", level=logging.DEBUG)


class PonthonProtocol(LanguageServerProtocol):
    """Override default LSP protocol (pygls) to link our reference server."""

    def bf_initialize(self, params: InitializeParams):
        """Called when the Language Server starts.
       Start Reference Server for given projects."""

        if not params.rootPath and not params.rootUri:
            logging.error("Language Client might have a problem! rootPath or rootUri is required.")
            exit(1)

        rootPath = str(params.rootUri)
        if not rootPath:
            rootPath = str(params.rootPath)

        rootPath = urlparse(rootPath).path

        logging.info(f"Workspace path is {rootPath}")

        projectManager = ProjectManager()
        self.project = projectManager.lsp_add_workspace(rootPath)

        if not self.project:
            logging.error("Couldn't load workspace.")
            exit(1)

        logging.info("Ponthon Language Server initialized.")
        return super().bf_initialize(params)


class Ponthon(LanguageServer):
    """Our Language Server."""

    def __init__(self):
        super().__init__(protocol_cls=PonthonProtocol)

    @property
    def project(self):
        return self.lsp.project


ponthon = Ponthon()


@ponthon.feature(COMPLETION, trigger_characters=['.'])
def completions(ls, params: CompletionParams = None):
    """Returns completion items."""
    if not params:
        return CompletionList(False, [])

    parser = CompletionParser(params, ls)
    return parser.complete()

@ponthon.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    """Update given Module if its a valid python file."""

    document_path = Path(urlparse(params.textDocument.uri).path)
    module = ls.project.get_module(document_path)

    module.update(ls.workspace.get_document(params.textDocument.uri)._source)

    # We commit session for testing purpose (no need to do it, just want to see if DB updates accordingly.)
    ProjectManager().session.commit()
    
    #
    # with open("test.test", "w") as file:
    #     text = ls.workspace.get_document(params.textDocument.uri)
    #     file.write(text.source)
    #
    # logging.info(f"Document {documentPath} did change.")
