# Como Usar o aval-usuario.py

Script para análise detalhada de um usuário específico em um repositório específico.

## Execução Rápida

```bash
# Ative o ambiente virtual
source .venv/bin/activate

# Exemplo básico (sem IA - mais rápido)
python aval-usuario.py --repo unb-mds/2025-2-Squad01 --user seu-username --since 2025-08-01 --disable-ai

# Exemplo com IA completa (mais detalhado)
python aval-usuario.py --repo unb-mds/2025-2-Squad01 --user seu-username --since 2025-08-01

# Especificar arquivo de saída
python aval-usuario.py --repo unb-mds/2025-2-Squad01 --user seu-username --since 2025-08-01 --out meu-relatorio.md
```

## Argumentos

| Argumento | Descrição | Obrigatório | Exemplo |
|-----------|-----------|-------------|---------|
| `--repo` | Repositório (owner/repo) | ✅ | `unb-mds/2025-2-Squad01` |
| `--user` | Username do GitHub | ✅ | `seu-username` |
| `--since` | Data início (YYYY-MM-DD) | ✅ | `2025-08-01` |
| `--token` | Token GitHub | ❌ | (use .env) |
| `--openai-key` | Chave OpenAI | ❌ | (use .env) |
| `--disable-ai` | Desabilitar IA | ❌ | - |
| `--out` | Arquivo saída | ❌ | `relatorio.md` |

## O que o Script Faz

### Coleta de Dados
- **Commits**: Mensagens, estatísticas, arquivos modificados
- **Issues**: Títulos, descrições, labels, comentários
- **Pull Requests**: Detalhes, estatísticas de código
- **Revisões**: Comentários de revisão de código

### Análise com IA
- **Qualidade de Commits**: Clareza, atomicidade, convenções
- **Qualidade de Issues**: Critérios de aceitação, formato
- **Qualidade de Revisões**: Construtividade, especificidade

### Relatório Gerado
- Arquivo Markdown com análise completa
- Estatísticas detalhadas
- Recomendações específicas
- Exemplos dos últimos commits/issues/PRs

## Tempo de Execução

- **Sem IA**: 30-60 segundos
- **Com IA**: 2-5 minutos (depende da quantidade de dados)

## Exemplos Práticos

### Para um Projeto de Squad
```bash
python aval-usuario.py \
  --repo unb-mds/2025-2-Squad01 \
  --user joaosilva \
  --since 2025-08-01 \
  --out joao-squad01-report.md
```

### Para Análise Rápida (Sem IA)
```bash
python aval-usuario.py \
  --repo unb-mds/DFemObras \
  --user mariadev \
  --since 2025-07-01 \
  --disable-ai
```

### Para Múltiplos Usuários (Script Bash)
```bash
#!/bin/bash
REPO="unb-mds/2025-2-Squad01"
USERS=("user1" "user2" "user3")

for user in "${USERS[@]}"; do
  echo "Analisando $user..."
  python aval-usuario.py --repo $REPO --user $user --since 2025-08-01
done
```

## Saída Esperada

O script gera um arquivo Markdown com:

### Resumo Executivo
- Estatísticas gerais (commits, issues, PRs, revisões)
- Pontuações de qualidade IA
- Métricas de produtividade

### Análises Detalhadas
- **Commits**: Qualidade das mensagens, recomendações
- **Issues**: Estrutura das histórias, critérios de aceitação
- **Revisões**: Qualidade do feedback, colaboração

### Recomendações
- Pontos fortes identificados
- Áreas de melhoria específicas
- Próximos passos sugeridos

## Solução de Problemas

### Token Inválido
```bash
# Teste seu token
curl -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/user
```

### Usuário Não Encontrado
- Verifique se o username está correto
- Confirme se o usuário tem atividade no repositório no período

### Repositório Privado
- Certifique-se que seu token tem acesso ao repositório
- Para tokens fine-grained, configure as permissões corretas

## Dicas de Uso

1. **Comece sem IA** para teste rápido
2. **Use datas recentes** para análise mais relevante
3. **Analise repositórios ativos** para mais dados
4. **Compare múltiplos usuários** do mesmo projeto
5. **Execute mensalmente** para acompanhar evolução
