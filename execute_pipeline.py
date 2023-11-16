import papermill as pm


# pm.execute_notebook(
#     "pegar_dados_youtube - dev.ipynb",
#     "pegar_dados_youtube - dev - out.ipynb",
#     parameters={},
# )

pm.execute_notebook("transform.ipynb", "transform.ipynb", parameters={})
