import papermill as pm

# antes de rodar, instalar os pacotes
# pip install -r requirements.txt

pm.execute_notebook(
    "pegar_dados_youtube - dev.ipynb",
    "pegar_dados_youtube - dev - out.ipynb",
    parameters={},
)

pm.execute_notebook("transform.ipynb", "transform.ipynb", parameters={})
