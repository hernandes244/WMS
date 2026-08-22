# WMS

Sistema de gerenciamento de armazém (WMS) com estoque, recebimento detalhado, movimentações, pedidos, geração de separação e dashboards.

## Stack
- Python 3.12 + Django 5
- PostgreSQL
- Bootstrap 5 + Chart.js
- Docker / Docker Compose

## Módulos
- Dashboard operacional
- Cadastro de produtos e endereços
- Estoque por produto/endereço/lote
- Entrada de mercadorias com conferência
- Movimentação interna
- Pedidos e itens
- Geração de separações por pedido
- Histórico de movimentações
- Administração Django

## Executar com Docker

```bash
docker compose up --build
```

Depois acesse `http://localhost:8000`.

Criar usuário administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

## Executar localmente

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

O projeto é um MVP funcional e foi estruturado para evoluir para operação por coletor Android, leitores de código de barras/IMEI, ondas de separação, packing e expedição.