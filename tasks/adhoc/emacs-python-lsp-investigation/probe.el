;; Load the real init.el, open a gacalc file, start lsp-mode, and print which
;; servers attached and what completion returns after `g3.e_1.`. Run by run_probe.sh.
(setq lsp-restart 'ignore)
(load-file "~/.emacs.d/init.el")
(find-file "/gacalc/src/gacalc/frame.py")
(python-mode)
(lsp)
(let ((deadline (+ (float-time) 90)))
  (while (and (< (float-time) deadline)
              (not (and (lsp-workspaces)
                        (eq (lsp--workspace-status (car (lsp-workspaces))) 'initialized))))
    (accept-process-output nil 0.5)))
(message "PROBE servers: %S"
         (mapcar (lambda (w) (lsp--client-server-id (lsp--workspace-client w))) (lsp-workspaces)))
(setq buffer-read-only nil)
(message "PROBE company-backends: %S" company-backends)
(message "PROBE capf: %S" completion-at-point-functions)
(goto-char (point-max))
(insert "\nfrom gacalc import g3\ng3.e_1.")
(sleep-for 3)
(let ((res (ignore-errors
             (lsp-request "textDocument/completion"
                          (lsp--text-document-position-params)))))
  (message "PROBE completion: %S"
           (mapcar (lambda (i) (lsp:completion-item-label i))
                   (if (lsp-completion-list? res) (lsp:completion-list-items res) res))))
(set-buffer-modified-p nil)
(kill-emacs 0)
