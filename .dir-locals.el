((python-mode
  . ((eglot-workspace-configuration
      . (:pylsp (:plugins
                 (:ruff
                  (:enabled t
                   :formatEnabled t))
                 (:pylsp_mypy
                  (:enabled t))))))))
