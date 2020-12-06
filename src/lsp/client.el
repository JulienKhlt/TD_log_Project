(lsp-register-client
 (make-lsp-client :new-connection (lsp-stdio-connection '("python" "~/Projects/TD_log_Project/python-extension/server"))
                  :major-modes '(python-mode)
                  :priority 1
                  :server-id 'ponthon))
