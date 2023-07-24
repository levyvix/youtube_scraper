import papermill as pm

pm.execute_notebook(
    "pegar_dados_youtube.ipynb",
    "pegar_dados_youtube.ipynb",
    parameters=dict(),
)

pm.execute_notebook(
    "criar_tabela_unica.ipynb",
    "criar_tabela_unica.ipynb",
    parameters=dict(),
)
