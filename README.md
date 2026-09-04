# WMS

Sistema de gerenciamento de armazém (WMS) com estoque, recebimento detalhado, armazenagem, inventário, pedidos, separação, dashboards e operação mobile por smartphone.

## Stack
- Python 3.12 + Django 5
- Django REST Framework + Token Authentication
- PostgreSQL
- Docker / Docker Compose
- WMS Mobile responsivo
- Câmera do celular para EAN, QR Code, Code 128 e IMEI

## Operação pelo celular
Abra `/mobile/` no navegador do Android. O mesmo backend atende o painel web e o mobile.

### Recebimento
- Seleção da entrada
- Leitura do produto pela câmera
- Quantidade
- Lote e validade
- Endereço de destino
- Controle de IMEI quando o produto exigir
- Atualização automática do estoque e histórico

### Armazenagem / movimentação
- Produto por câmera
- Origem
- Quantidade
- Destino
- Validação de saldo disponível
- Registro da movimentação
- Transferência de IMEIs quando aplicável

### Inventário
- Produto por câmera
- Endereço
- Quantidade contada
- Lote opcional
- Ajuste automático do saldo
- Registro da diferença no histórico

### Separação
- Consulta de pedidos pendentes
- Seleção de um ou vários pedidos
- Geração automática da separação por endereço e estoque disponível
- Reserva do estoque
- Tarefa guiada por endereço/produto
- Bloqueio de produto errado
- Bloqueio de endereço errado
- Controle de quantidade
- Baixa da reserva ao separar
- Atualização do status da separação e do pedido

### IMEI
- 15 dígitos
- Somente numérico
- Validação Luhn
- Verificação de cadastro
- Verificação do produto associado
- Verificação de status
- Bloqueio de IMEI duplicado no recebimento

## API mobile
- `POST /api/mobile/login/`
- `GET /api/mobile/me/`
- `GET /api/mobile/scan/?code=...`
- `GET /api/mobile/addresses/`
- `GET /api/mobile/receipts/`
- `POST /api/mobile/receive/`
- `POST /api/mobile/transfer/`
- `POST /api/mobile/inventory/`
- `GET /api/mobile/orders/`
- `POST /api/mobile/picking/create/`
- `GET /api/mobile/pickings/`
- `POST /api/mobile/picking/pick/`
- `POST /api/mobile/imei/validate/`

Rotas protegidas usam `Authorization: Token <token>`.

## Banco de dados
A migração `0002_mobile.py` cria as estruturas de códigos de barras e IMEI. Depois de atualizar o projeto, execute:

```bash
python manage.py migrate
```

Com Docker:

```bash
docker compose up --build
```

E, se necessário:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Acesso no celular
Em produção, publique o WMS com HTTPS e acesse:

`https://SEU-DOMINIO/mobile/`

A câmera do navegador exige contexto seguro. Em desenvolvimento, `localhost` funciona no próprio aparelho; acessar um IP HTTP de outro dispositivo pode impedir o acesso à câmera.

## Próximas etapas
A base agora está preparada para receber som, vibração, confirmação visual, modo offline com fila de sincronização, conferência, expedição, impressão de etiquetas, dashboards avançados e integração futura com coletores Zebra/Urovo sem trocar a API central.
