# WMS

Sistema de gerenciamento de armazém (WMS) com estoque, recebimento detalhado, movimentações, pedidos, separação e dashboards.

## Stack
- Python 3.12 + Django 5
- Django REST Framework + Token Authentication
- PostgreSQL
- Docker / Docker Compose
- WMS Mobile em PWA responsiva
- Câmera do celular para leitura de códigos

## Módulos
- Dashboard operacional
- Cadastro de produtos, códigos de barras e endereços
- Estoque por produto/endereço/lote
- Entrada de mercadorias
- Movimentação interna
- Pedidos e itens
- Separação por pedido
- Histórico de movimentações
- Administração Django
- API autenticada para operação mobile
- Consulta de produto por EAN/QR/Code
- Transferência de estoque pelo celular

## WMS pelo celular
Abra `/mobile/` no navegador do Android. O operador faz login e pode:

1. Tocar em **ABRIR CÂMERA**.
2. Ler EAN, Code 128, QR Code e outros formatos suportados pela biblioteca de câmera.
3. Consultar produto e estoque por endereço.
4. Fazer transferência de estoque pelo celular.

A câmera exige um contexto seguro no navegador. Em produção, use HTTPS. Para desenvolvimento, `localhost` é permitido pelos navegadores modernos; acessar por IP HTTP a partir de outro celular pode bloquear a câmera.

## API mobile
- `POST /api/mobile/login/`
- `GET /api/mobile/me/`
- `GET /api/mobile/scan/?code=...`
- `GET /api/mobile/addresses/`
- `POST /api/mobile/transfer/`

As rotas protegidas usam `Authorization: Token <token>`.

## Executar com Docker

```bash
docker compose up --build
```

Depois acesse `http://localhost:8000` no computador.

Criar usuário administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

Depois cadastre produtos, endereços e códigos de barras em `/admin/`.

## Executar localmente

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Próxima evolução
A arquitetura está preparada para evoluir o celular/PWA para aplicativo Android nativo, adicionar recebimento completo, inventário, separação guiada, conferência, expedição, IMEI, operação offline e sincronização.
