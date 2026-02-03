# Padrões N8N + PostgreSQL

## Expressions Corretas em PostgreSQL Node

### SELECT com variável
```sql
SELECT * FROM leads WHERE phone = '{{ $json.phone }}'
```
⚠️ SEMPRE aspas simples ao redor de {{ }} para strings

### UPSERT (Insert or Update)
```sql
INSERT INTO leads (phone, name, stage, updated_at)
VALUES ('{{ $json.phone }}', '{{ $json.name }}', '{{ $json.stage }}', NOW())
ON CONFLICT (phone) DO UPDATE SET
  name = EXCLUDED.name,
  stage = EXCLUDED.stage,
  updated_at = NOW()
```

### Buscar histórico de mensagens
```sql
SELECT role, content, created_at 
FROM messages 
WHERE lead_phone = '{{ $json.phone }}'
ORDER BY created_at DESC
LIMIT 20
```

### Atualizar estágio do funil
```sql
UPDATE leads SET 
  stage = '{{ $json.new_stage }}',
  last_interaction = NOW(),
  interaction_count = interaction_count + 1
WHERE phone = '{{ $json.phone }}'
```

## Armadilhas Comuns
1. **Aspas**: PostgreSQL usa aspas SIMPLES para strings. Aspas duplas são para identificadores.
2. **NULL handling**: Use COALESCE para defaults
3. **Injection**: N8N expressions são interpoladas, cuidado com input do usuário
4. **Timestamps**: Use `NOW()` ao invés de enviar do N8N para consistência
5. **JSONB**: Para dados flexíveis, use campos JSONB com operadores `->` e `->>`
