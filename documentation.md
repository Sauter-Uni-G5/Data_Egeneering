# Documentação do Projeto

## 1. Resumo Executivo

*[Insira aqui um resumo de alto nível do projeto, seus objetivos e os principais resultados alcançados.]*

---

## 2. Casos de Uso

Abaixo estão os casos de uso definidos para este projeto, priorizados de acordo com as necessidades do negócio.

| ID | Caso de Uso | Prioridade | Descrição Detalhada |
|----|-------------|------------|---------------------|
| 1  | [Nome do Caso de Uso 1] | Alta | [Descrição detalhada do primeiro caso de uso] |
| 2  | [Nome do Caso de Uso 2] | Média | [Descrição detalhada do segundo caso de uso] |
| 3  | [Nome do Caso de Uso 3] | Baixa | [Descrição detalhada do terceiro caso de uso] |

---

## 3. Responsabilidades da Equipe

A equipe foi dividida da seguinte forma, com as responsabilidades detalhadas para cada membro.

### DevOps: Alcielma e Micaelle

| Membro | Tarefa | Commits Relevantes (Link) | Arquivos Modificados | Datas |
|---|---|---|---|---|
| **Alcielma** | Conexão com GCP | [Link para o commit] | `main.tf`, `variables.tf` | [Data] |
| **Alcielma** | Implementação de CI/CD com GitHub Actions | [Link para o commit] | `.github/workflows/deploy.yml` | [Data] |
| **Alcielma** | Criação do Dockerfile | [Link para o commit] | `Dockerfile` | [Data] |
| **Micaelle** | Provisionamento da infraestrutura com Terraform | [Link para o commit] | `main.tf`, `cloudrun.tf` | [Data] |
| **Ambas** | Configuração da API REST no Cloud Run | [Link para o commit] | `cloudrun.tf`, `service.yaml` | [Data] |

### Engenharia de Dados/Análise de Dados: Alan e Diogenys

| Membro | Tarefa | Commits Relevantes (Link) | Arquivos Modificados | Datas |
|---|---|---|---|---|
| **Alan** | Definição do esquema do banco de dados | [Link para o commit] | `schema.sql` | [Data] |
| **Diogenys** | Criação das tabelas no BigQuery | [Link para o commit] | `scripts/create_tables.sql` | [Data] |
| **Ambos** | Desenvolvimento das queries de ETL | [Link para o commit] | `queries/etl.sql` | [Data] |

### Machine Learning: Luís

| Membro | Tarefa | Commits Relevantes (Link) | Arquivos Modificados | Datas |
|---|---|---|---|---|
| **Luís** | Desenvolvimento do modelo de Machine Learning | [Link para o commit] | `model/train.py`, `model/predict.py` | [Data] |
| **Luís** | Análise de Dados Exploratória (ADE) | [Link para o commit] | `notebooks/data_exploration.ipynb` | [Data] |

### IAM (Identity and Access Management): Alan e Micaelle

| Membro | Tarefa | Commits Relevantes (Link) | Arquivos Modificados | Datas |
|---|---|---|---|---|
| **Alan** | Definição das roles e permissões | [Link para o commit] | `iam.tf` | [Data] |
| **Micaelle** | Configuração das Service Accounts | [Link para o commit] | `iam.tf` | [Data] |

### Alertas e Monitoramento (Looking): Alcielma

| Membro | Tarefa | Commits Relevantes (Link) | Arquivos Modificados | Datas |
|---|---|---|---|---|
| **Alcielma** | Configuração de alertas no Google Cloud Monitoring | [Link para o commit] | `monitoring.tf` | [Data] |

### Dashboard: Micaelle

| Membro | Tarefa | Commits Relevantes (Link) | Arquivos Modificados | Datas |
|---|---|---|---|---|
| **Micaelle** | Criação de dashboards no Google Cloud Monitoring/Looker Studio | [Link para o commit] | `dashboards/main_dashboard.json` | [Data] |

---

## 4. Diagramas

Aqui estão os diagramas que ilustram a arquitetura, o fluxo de dados, o processo de deploy e a sequência de chamadas da aplicação.

### 4.1. Diagrama de Arquitetura

*[Insira aqui o diagrama de arquitetura. Pode ser uma imagem ou um link para uma ferramenta como o Lucidchart/Miro.]*
![Diagrama de Arquitetura](https://via.placeholder.com/800x400.png?text=Diagrama+de+Arquitetura)

### 4.2. Diagrama de Fluxo de Dados

*[Insira aqui o diagrama de fluxo de dados.]*
![Diagrama de Fluxo de Dados](https://via.placeholder.com/800x400.png?text=Diagrama+de+Fluxo+de+Dados)

### 4.3. Diagrama de Deploy (CI/CD)

*[Insira aqui o diagrama do pipeline de CI/CD.]*
![Diagrama de Deploy](https://via.placeholder.com/800x400.png?text=Diagrama+de+Deploy)

### 4.4. Diagrama de Sequência de Chamadas

*[Insira aqui um diagrama de sequência para uma requisição típica na API.]*
![Diagrama de Sequência](https://via.placeholder.com/800x400.png?text=Diagrama+de+Sequência)

---

## 5. Guia de Implementação (README)

Esta seção detalha como configurar, rodar, testar e fazer o deploy da aplicação.

### 5.1. Pré-requisitos

*   [Liste aqui as ferramentas necessárias, ex: Docker, gcloud CLI, Terraform, Python 3.9+, etc.]
*   [Versões específicas, se houver.]

### 5.2. Setup Local

1.  Clone o repositório:
    ```bash
    git clone [URL_DO_REPOSITORIO]
    cd [NOME_DO_REPOSITORIO]
    ```
2.  Crie e configure o arquivo de variáveis de ambiente:
    ```bash
    cp .env.example .env
    ```
3.  Preencha as variáveis no arquivo `.env` com os valores corretos.
4.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### 5.3. Como Rodar a Aplicação

```bash
# Exemplo para uma aplicação Python/Flask
export FLASK_APP=main.py
flask run
```

### 5.4. Como Rodar os Testes

```bash
# Exemplo para testes com pytest
pytest
```

### 5.5. Como Treinar o Modelo de ML

```bash
python model/train.py --input-data [CAMINHO_PARA_OS_DADOS] --output-model [CAMINHO_PARA_SALVAR_O_MODELO]
```

### 5.6. Como Avaliar o Modelo

```bash
python model/evaluate.py --model [CAMINHO_PARA_O_MODELO] --test-data [CAMINHO_PARA_DADOS_DE_TESTE]
```

### 5.7. Como Fazer o Deploy

O deploy é automatizado via GitHub Actions. Um push para a branch `main` irá disparar o workflow de deploy.

Para deploy manual, siga os passos:
1.  Autentique-se no GCP:
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
2.  Inicialize o Terraform:
    ```bash
    terraform init
    ```
3.  Aplique a infraestrutura:
    ```bash
    terraform apply
    ```

### 5.8. Como Validar em Produção

*   Acesse a URL da API no Cloud Run: `[URL_DA_API]`
*   Verifique os logs no Google Cloud Logging.
*   Monitore o dashboard de métricas: `[LINK_PARA_O_DASHBOARD]`

### 5.9. Plano de Reversão (Rollback)

*   **Cloud Run:** Faça o deploy da versão anterior através da interface do Cloud Run ou via gcloud CLI.
*   **Terraform:** Para reverter uma mudança na infraestrutura, utilize `terraform apply` com um commit anterior da configuração.

---

## 6. Testes e Validação

### 6.1. Estratégia de Testes

*   **Testes Unitários:** Foco em funções individuais e classes.
*   **Testes de Integração:** Validação da interação entre componentes (ex: API e banco de dados).
*   **Testes de Contrato (API):** Verificação do schema de requests e responses.

### 6.2. Resultados dos Testes

*[Anexe aqui os resultados dos testes. Pode ser um screenshot, um log ou um link para o relatório de testes no CI/CD.]*

| Tipo de Teste | Entradas | Saídas Esperadas | Métricas | Thresholds |
|---|---|---|---|---|
| Unitário | `funcao_x(2)` | `4` | Cobertura de Código | > 80% |
| Integração | `POST /users` | `201 Created` | Latência | < 200ms |

### 6.3. Versões de Dataset

| Versão | Data | Descrição | Link/Localização |
|---|---|---|---|
| `v1.0` | [Data] | Dataset inicial para treinamento. | `gs://[BUCKET]/datasets/v1.0` |
| `v1.1` | [Data] | Dataset com dados atualizados. | `gs://[BUCKET]/datasets/v1.1` |

---

## 7. Observabilidade

### 7.1. Logs

*   **Onde ver:** Google Cloud Logging, filtrando pelo serviço do Cloud Run `[NOME_DO_SERVICO]`.
*   **Link:** `[LINK_DIRETO_PARA_OS_LOGS]`

### 7.2. Métricas e Dashboards

*   **Onde ver:** Google Cloud Monitoring e [Looker Studio/Outra ferramenta].
*   **Link para o Dashboard Principal:** `[LINK_PARA_O_DASHBOARD]`

### 7.3. Runbook de Incidentes

| Incidente Comum | Passos para Mitigação | Responsável |
|---|---|---|
| **API com alta latência (>500ms)** | 1. Verificar logs por erros. <br> 2. Escalar o número de instâncias no Cloud Run. <br> 3. Analisar queries lentas no BigQuery. | On-call DevOps |
| **Erro 5xx na API** | 1. Verificar logs da aplicação por stack traces. <br> 2. Fazer rollback para a versão anterior se for um problema de deploy. | On-call DevOps |
| **Modelo com baixa acurácia** | 1. Disparar o pipeline de retreinamento com novos dados. <br> 2. Notificar a equipe de ML. | On-call ML |

---

## 8. Segurança

### 8.1. Gerenciamento de Segredos

*   **Nunca commitar segredos no repositório.**
*   Utilizar um arquivo `.env` para desenvolvimento local, com um `.env.example` como template.
*   Em produção, os segredos são gerenciados pelo Google Secret Manager e injetados no Cloud Run como variáveis de ambiente.

### 8.2. Permissões Mínimas (IAM)

A aplicação segue o princípio do privilégio mínimo. As permissões necessárias são:

| Service Account | Permissões | Justificativa |
|---|---|---|
| `sa-cloud-run` | `roles/run.invoker` | Permitir acesso público à API. |
| `sa-cloud-run` | `roles/bigquery.dataViewer` | Acesso de leitura ao BigQuery. |
| `sa-github-actions` | `roles/run.admin` | Permissão para deploy no Cloud Run. |
| `sa-github-actions` | `roles/storage.admin` | Permissão para upload de artefatos. |

---

## 9. Registro de Decisões Arquiteturais (ADR)

| Decisão | Alternativas Consideradas | Data | Responsável |
|---|---|---|---|
| **Uso do Cloud Run para a API** | App Engine, GKE | [Data] | Alcielma, Micaelle |
| **Uso do BigQuery como Data Warehouse** | PostgreSQL (Cloud SQL), Redshift | [Data] | Alan, Diogenys |
| **Uso do Terraform para IaC** | Pulumi, gcloud scripts | [Data] | Micaelle |

---

## 10. Changelog

### v1.0.0 - [Data]

*   **Added:** Implementação inicial da API.
*   **Added:** Pipeline de CI/CD para deploy no Cloud Run.
*   **Added:** Modelo de ML v1.