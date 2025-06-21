# USS (UAS Service Supplier) Kit PoC

É um conjunto de dois programas criados para demonstrar como um provedor poderia implementar uma API e um Visualizador para interagir com o Discovery and Synchronization Service (DSS) e criar planos de voos, restrições e subscriptions, além de conseguir visualizar potenciais conflitos com áreas ja reservadas. A da API do USS, seguiu as especificações ASTM Standard Specification for UAS Traffic Management (UTM) UAS Service Supplier (USS) Interoperability e Standard Specification for Remote ID and Tracking. 

O desenvolvimento surgiu da necessidade de demonstrar a provedores de maneiras prática como é possível fazer a interação com o servidor de autenticação, com o DSS e com outros USSs para realização de desconflitos. Além disso o Visualizador foi criado para promover uma primeira versão de ferramenta que pode ser utilizada para realizar planejamento de voos em 3D.

O Visualizador interage diretamente com a API para efetivar os planos de voo, e que por sua vez possui um banco de dados próprio para armazenar os voos reservados e prover informação para outros USSs que possam precisar dela.

Acesse uma instancia do Visualizador em: [link](http://34.9.130.218/)
 
O repositório para acesso do código está disponível em: [Github](https://github.com/dp-icea/uss-kit-poc)

## Introdução

O projeto involve dois serviços principais, a API e o Visualizador, porém possui um serviço extra de banco de dados MongoDB, Para executar as ferramentas inclusas no USS Suite em sua máquina e em um ambiente remoto, siga os passos descritos abaixo.

### Pré-Requisitos
- Cesium Library API Token disponível em: [link](https://cesium.com/learn/ion/cesium-ion-access-tokens/)
- DSS Access Token.

#### Deploy Local
Existem duas formas de fazer o deploy local dos serviços fornecidos, utilizando o arquivo `docker-compose.dev.yml` criado, ou fazendo o deploy separado de cada serviço

**Docker Compose**

Para utilizar o deploy com Docker Compose:

Instale a ferramenta Docker: (link)[https://docs.docker.com/compose/install/] 

Utilize o comando `docker compose -f docker-compose.dev.yml up` na raiz do projet

**Rodar Separadamente**

As seguintes informações foram testadas no sistema operacional Ubuntu 22.04.

1. Banco de Dados
    1. Instale o mongod (Versão testada 8.0.10): (link)[https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/] 
    2. Crie um diretório que conterá o conteúdo do banco de dados e execute o banco de dados. Ex: `mongod --dbpath ./db`

2. API
    1. Instale o Python (Versão testada 3.10.12): (link)[https://python.org.br/instalacao-linux/] 
    2. Instale as bibliotecas descritas no arquivo `requirements.txt`
    3. Execute a api em modo de desenvolvimento. Ex: `python main.py`

3. Visualizador
    1. Instale o Node (Versão testada: 22.15.0): (link)[https://nodejs.org/en/download] 
    2. Instale as bibliotecas e rode o ambiente de desenvolvimento. Ex: `npm run dev`
    3. Deploy Produção

#### Deploy Produção

Em produção, foi configurado um serviço Docker Swarm orquestrado pelo Portainer. Utilizamos a infraestrutura de CICD do Github Actions e definimos um serviço de registro de images do Docker de forma local, alem de configurar um runner também local.

O arquivo de descrição do pipeline pode ser encontrado na pasta `.github/workflows/deploy.yml` e arquivo de descrição da Stack pode ser encontrado no arquivo `docker-compose.yml` na raiz do repositório.
