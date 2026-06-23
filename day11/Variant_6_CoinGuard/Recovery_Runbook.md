# Disaster Recovery Runbook

## Сценарий 1. Полный отказ дата-центра

Шаг 1. Развернуть инфраструктуру

terraform apply -auto-approve

Шаг 2. Восстановить Bitcoin Node

restore_btc_snapshot.sh

Шаг 3. Восстановить Ethereum Node

restore_eth_snapshot.sh

Шаг 4. Восстановить Solana Node

restore_solana_snapshot.sh

Шаг 5. Скачать снапшот Matching Engine

aws s3 cp s3://coinguard-backups/engine/latest.snapshot /tmp/

Шаг 6. Восстановить движок

./matching-engine --restore /tmp/latest.snapshot

Шаг 7. Применить WAL

./replay_wal --source kafka

Шаг 8. Проверить балансы

SELECT wallet_id,balance FROM wallets;

Шаг 9. Включить торговлю

exchange enable deposits
exchange enable withdrawals

Ожидаемое время восстановления: 3 часа.