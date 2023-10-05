import papermill as pm


pm.execute_notebook(
    "pegar_dados_youtube.ipynb", "pegar_dados_youtube.ipynb", parameters={}
)

pm.execute_notebook("transform.ipynb", "transform.ipynb", parameters={})


