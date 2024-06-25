# Transition to a Modern Data Platform for Swastik
This project outlines the solution for Swastik transition from a traditional database system to a modern data platform, primarily leveraging the Azure platform and GitHub for orchestration and version control.

### Primary ETL Pipeline:
Metadata-driven Source system(MySQl database with stored procedure defines metadata) --> Azure Data Factory Extraction(metadata) --> Landing Zone (Blob Storage) --> Databricks Transformation (Inclusive Unit tests) --> Data Hub (Datalake Storage) 

### Orchestrator / CICD pipeline :
GitHub Actions Workflow --> main branch: InfraDeployment --> local_dev branch: Databricks jobs (on schedule) Deployment (also on pull request) --> ADF branch: Azure Data Factory pipelines (on schedule) Deployment (also on push)

### Local Project Setup:
#### 1. Clone github repo to local machine;
#### 2. Initialize a metadata-driven MySQL database and populate with sample data:
   - Requirement: MySQL server installed;
   - Mannul step: Create python venv and install necessary packages (docker would be overkill) ;
   - Command: pip install python-dotenv pandas mysql-connector-python;
   - Populate database: set your localhost and credentials in .env and run init_local_mysql.py;
#### 3. Deploy Infrastructures (Within same resourcegroup: Azure Data Factory, Databrick, KeyVault resources) in Azure platform:
   - Requirement: Azure Subscription, Set Azure_credentials(clientID,clientSecret,subscriptionID,tenantID) in Github repo/Secrets and Variables/Actions;
   - Mannul step: Run Github Actions/InfraDeploy.yml workflow, select Initialize-KeyVault Mode;
   - Mannul step: Link Databrick repo with Github repo; Link Data Factory repo with Github repo;
#### 4. Initialize Azure Data Factory based resources:
   - Process: check the pipeline, 2 associated datasets, 2 associated linkedservices and 1 IntegrationRuntime. Due to authentication complexity, in the first run of ADFPipeline.yml workflow:
     2 linkedservices will be automatically built, however you need to provide them the correct credentials. The rest resources(depends on linkedServices) will be built in following runs;
   - Triggering: you can mannuly trigger this pipeline in Github UI; or checkout ADF branch and check different resources and push (recommended);
   - Mannul step: provide linkedServices correct credentials; give permissions to ADF managed identity; replace secrets in KeyVaults;
#### 5. Deploy databricks job:
   - Process: workflow will deploy a cluster, src/notebooks and a job to the same databricks workspace from step3; this job will be triggered to run the notebooks which inclusive: mount storages, read df, aggregate new df, delta table, quality check and load to data hub;
   - Requirement: give permissions to databricks managed identity, or store KeyVault secrets to Databricks Secrets (recommended); replace secrets in KeyVaults; register databricks as resource provider etc;
   - Mannul step: Run Github Actions/main.yml workflow in Github UI (recommended); or checkout main branck and push trigger(pull request trigger needs another account to review);
### Further development:
#### 1. In the perspective of automating the solution:
   - ADF pipeline should take the mannully permission granting steps into consideration. One possiblity is integrated sdk to manage resources and permissions.
   - ADF and Databricks schedules should be decided by specific business logic, hence ADF sits in an apart branch with its own pipeline.
#### 2. In the perspective of enriching data engineering capabilities:
   - Databricks has good integration possibilities in terms of data quality/unit test tools.
   - Considering the consumption requirements, Synapse could be integrated for analyse workload. 
     
