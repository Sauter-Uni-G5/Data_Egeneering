# Data Engineering - API
## Responsáveis
 [Allan J.](https://github.com/allanjose001) | 
 [Ismael D.](https://github.com/ismael-ds-correia) |
 [Alcielma L.](https://github.com/Alcielma)

## Sobre
Projeto da Sauter University: AI Specialists Programs. Este projeto consiste em treinar um modelo de Machine Learning usando LightGBM com implementações feitas utilizando todas as devidas ferramentas do Google Cloud Plataform.

## Como configurar
### API: Data_engineer.
- Utilizar Python versão 3.10 ou superior.
- Instalar as bibliotecas listadas no requiriments.txt.
- Comando para rodar a API: uvicorn main:app --reload
- URL padrão: http://127.0.0.1:8000
### Tags e Endpoints:
 - /api/hydro
 - /api/ear
 - /api/weather
 - /api/registry
 - /api/pipeline
### Exemplo de URL
http://127.0.0.1:8000/api/hydro?package_id=<ID_DO_PACKAGE>&start_date=2020-01-01&end_date=2021-12-31&page=1&page_size=100
Parametros:
- package_id (obrigatório): O ID do pacote de dados no ONS.
- ano (opcional): Ano específico para filtrar os dados.
- mes (opcional): Mês específico para filtrar os dados.
- nome_reservatorio (opcional): Nome do reservatório para filtrar.
- start_date (opcional): Data inicial no formato YYYY-MM-DD.
- end_date (opcional): Data final no formato YYYY-MM-DD.
- page (opcional): Número da página (padrão: 1).
- page_size (opcional): Quantidade de registros por página (padrão: 100).

### Saida padrão de requisição:
{
  "data": [
    {
      "reservatorio": "Reservatório Y",
      "energia_armazenada": 78.9,
      "data": "2020-01-01"
    },
    ...
  ],
  "page": 1,
  "page_size": 50,
  "total_pages": 20
}

## Caso de uso
A principal funcionalidade desta API é utilizar sua Pipeline que coleta dados selecionados da ONS, faz a normalização, tratamento de colunas e agregação das tabelas e então gera um arquivo .parquet que é enviado de maneira versionada para um Bucket no Google Cloud Storage, e eventualmente importada para o Big Query, onde poderá ser utilizado em larga escala.

### Exemplo de URL da Pipeline
http://127.0.0.1:8000/api/pipeline/run?registry_package_id=a849a9c1-09b8-4b9b-84dc-5ac113043f37&ear_package_id=61e92787-9847-4731-8b73-e878eb5bc158&hydro_package_id=98a9aa79-06fe-4a9f-ac6b-04aa707bdfca&start_date=2020-01-01&end_date=2020-12-31


## Tecnologias Usadas

### <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" height="40" alt="java logo"/> [Python](https://www.python.org)
* Versão 3.8.10


# Terraform

## Sobre
Este módulo Terraform provisiona a infraestrutura necessária no Google Cloud Platform (GCP) para hospedar a API. Ele cria os recursos básicos de autenticação, banco de dados e execução do serviço em Cloud Run.

## Recursos Criados

Service Account com permissões para BigQuery, Artifact Registry e Cloud Run.

BigQuery: um Dataset e uma Tabela para armazenamento de dados.

Cloud Run: serviço que hospeda a API, configurado para receber a imagem do Artifact Registry.

Outputs úteis:

  URL do serviço no Cloud Run

  Service Account

  Dataset ID e Table ID do BigQuery

## Como configurar

Instale o Terraform
 (v0.13 ou superior).

Configure o Google Cloud SDK (gcloud auth application-default login).

Inicialize o Terraform:

## Como configurar

1.Instale o Terraform
 (v0.13 ou superior).

2.Configure o Google Cloud SDK (gcloud auth application-default login).

3.Inicialize o Terraform:
    terraform init
4.Aplique a configuração:
    terraform apply -auto-approve

## Variáveis Principais

-project: ID do projeto no GCP

-region: região de implantação (ex: us-central1)

-dataset_id: nome do Dataset no BigQuery

-table_id: nome da Tabela no BigQuery

-image_repo: caminho do repositório da imagem no Artifact Registry

-image_tag: tag da imagem (ex: latest)
