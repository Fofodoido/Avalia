# Avaliador de Qualidade de Práticas Ágeis v4.4

Uma ferramenta avançada para avaliar práticas de desenvolvimento ágil de software em organizações do GitHub usando métricas quantitativas e análise qualitativa com IA.

## Visão Geral

Esta ferramenta analisa repositórios do GitHub e contribuidores para avaliar a qualidade das práticas de desenvolvimento ágil. Combina métricas tradicionais (commits, issues, PRs, revisões de código) com análise de IA de mensagens de commit, descrições de issues e qualidade de revisão de código para fornecer pontuação abrangente de maturidade ágil.

## Principais Funcionalidades

### 🔍 **Análise Abrangente**
- **Sinais de Repositório**: README, licença, CI/CD, testes, documentação
- **Métricas de Contribuição**: Commits, issues, pull requests, comentários
- **Avaliação de Qualidade**: Issues/PRs maduros, commits atômicos, métricas de diversidade
- **Dinâmica de Equipe**: Padrões de atividade semanal, indicadores de colaboração

### 🤖 **Análise de Qualidade com IA** (Novo na v4.0)
- **Qualidade de Mensagens de Commit**: Avalia clareza, commits convencionais, mudanças atômicas
- **Qualidade de Issues/Histórias**: Avalia critérios de aceitação, formato de história de usuário, testabilidade
- **Qualidade de Revisão de Código**: Analisa construtividade, especificidade, tom colaborativo
- **Recomendações Inteligentes**: Sugestões de melhoria personalizadas

### 📊 **Pontuação Multi-Nível**
- **Pontuações Individuais**: Avaliação de maturidade ágil por usuário
- **Detalhes de Repositório**: Métricas granulares por repositório por usuário
- **Visão Organizacional**: Padrões e tendências de toda a equipe

## Instalação

### Pré-requisitos
- Python 3.8+
- Token de acesso à API do GitHub
- Chave da API OpenAI (opcional, para recursos de IA)

### Configuração
```bash
# Clone ou baixe o projeto
cd revisao-mds

# Crie ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure segredos
cp .env.example .env
# Edite .env com seus tokens
```

### Configuração do Ambiente
Crie um arquivo `.env` com suas chaves de API:
```bash
# Token do GitHub (obrigatório)
GH_TOKEN=github_pat_seu_token_aqui

# Chave da API OpenAI (opcional, para análise de IA)
OPENAI_API_KEY=sk-proj-sua_chave_aqui
```

## Uso

### Uso Básico
```bash
# Analise organização desde data específica
python aval-mds.py --org sua-org --since 2024-08-01 --out resultados.xlsx

# Com análise de IA habilitada
python aval-mds.py --org sua-org --since 2024-08-01 --out resultados.xlsx

# Sem análise de IA (mais rápido, menor custo)
python aval-mds.py --org sua-org --since 2024-08-01 --out resultados.xlsx --disable-ai
```

### Opções Avançadas
```bash
# Filtrar apenas repositórios recentes
python aval-mds.py --org sua-org --since 2024-08-01 --only-recent --skip-forks

# Incluir repositórios criados a partir da data especificada
python aval-mds.py --org sua-org --since 2024-08-01 --include-new-repos

# Analisar usuários específicos
python aval-mds.py --org sua-org --since 2024-08-01 --users-csv usuarios.csv

# Ajustar performance
python aval-mds.py --org sua-org --since 2024-08-01 --workers 4

# Depurar problemas de autenticação
python aval-mds.py --org sua-org --since 2024-08-01 --debug-auth
```

### Argumentos da Linha de Comando
| Argumento | Descrição | Obrigatório |
|-----------|-----------|-------------|
| `--org` | Nome da organização GitHub | ✅ |
| `--since` | Data de início (AAAA-MM-DD) | ✅ |
| `--out` | Arquivo Excel de saída | Não (padrão: avaliacao.xlsx) |
| `--token` | Token GitHub (ou use env GH_TOKEN) | Não |
| `--openai-key` | Chave OpenAI (ou use env OPENAI_API_KEY) | Não |
| `--disable-ai` | Desabilitar análise de IA | Não |
| `--workers` | Workers concorrentes | Não (padrão: 8) |
| `--skip-forks` | Pular repositórios fork | Não |
| `--only-recent` | Pular repos com atividade antiga | Não |
| `--include-new-repos` | Incluir repos criados desde --since | Não |
| `--users-csv` | Arquivo CSV com coluna github_username | Não |
| `--debug-auth` | Mostrar diagnósticos de autenticação | Não |

## Formato de Saída

A ferramenta gera um arquivo Excel com três planilhas:

### 1. **Resumo_por_usuario** (Resumo do Usuário)
Pontuações e métricas agregadas por usuário:
- `github_username`: Identificador do usuário
- `score_final_0_1`: Pontuação geral de maturidade ágil (0.0-1.0)
- `nivel`: Nível de maturidade (Maduro/Saudável/Iniciante)
- `explicacao_geral`: Explicação resumida da avaliação em linguagem natural
- `commits_total`, `issues_total`, `prs_total`: Contadores de atividade
- `mature_issues_total`, `mature_prs_total`: Indicadores de qualidade
- `atomicity_media`: Atomicidade média de commits
- `ai_commit_quality_media`: Qualidade de mensagens de commit avaliada por IA
- `ai_issue_quality_media`: Qualidade de issues/histórias avaliada por IA
- `ai_review_quality_media`: Qualidade de revisão de código avaliada por IA

### 2. **Detalhes_por_repo** (Detalhes do Repositório)
Métricas detalhadas por usuário por repositório:
- Metadados do repositório (nome, linguagem, estrelas, etc.)
- Contadores de contribuição individual
- Sinais de qualidade do repositório (README, testes, CI/CD, etc.)
- Componentes de pontuação detalhados
- Avaliações de qualidade de IA por repositório

### 3. **Proveniencia** (Proveniência)
Metadados da análise:
- Organização e intervalo de datas
- Parâmetros de configuração
- Pesos de pontuação e metas
- Timestamp de geração

## Metodologia de Pontuação

### Métricas Principais (Tradicionais)
- **Atividade Semanal**: Commits, issues, PRs, comentários consistentes
- **Indicadores de Qualidade**: Issues/PRs maduros com discussão adequada
- **Práticas Técnicas**: Commits atômicos, tipos diversos de issues
- **Saúde do Repositório**: Documentação, testes, configuração CI/CD

### Métricas Aprimoradas por IA (Novo)
- **Qualidade de Commits**: Clareza, formato convencional, mudanças atômicas
- **Qualidade de Issues**: Critérios de aceitação, formato de história de usuário, testabilidade
- **Qualidade de Revisão**: Feedback construtivo, sugestões específicas

### Níveis de Maturidade
- **Maduro** (≥75%): Excelentes práticas ágeis
- **Saudável** (45-74%): Boas práticas com espaço para melhoria
- **Iniciante** (<45%): Práticas básicas, precisa de desenvolvimento

## Detalhes da Análise de IA

### Análise de Mensagens de Commit
Avalia baseado em:
- **Clareza**: Mensagens claras e descritivas
- **Especificidade**: Informações detalhadas sobre o que/por que
- **Commits Convencionais**: Seguindo formatos padrão
- **Atomicidade**: Mudanças de propósito único

### Análise de Issues/Histórias
Avalia:
- **Critérios de Aceitação**: Requisitos claros e testáveis
- **Formato de História de Usuário**: Estrutura adequada "Como... Eu quero... Para que..."
- **Detalhes Suficientes**: Contexto e requisitos completos
- **Testabilidade**: Critérios de conclusão verificáveis

### Análise de Revisão de Código
Examina:
- **Construtividade**: Feedback útil e acionável
- **Especificidade**: Sugestões e explicações detalhadas
- **Cobertura**: Aborda qualidade, segurança, performance
- **Colaboração**: Tom profissional e solidário

## Requisitos do Token GitHub

### Token Fine-Grained (Recomendado)
- **Resource Owner**: Organização alvo
- **Acesso a Repositório**: Todos os repositórios para analisar
- **Permissões (Leitura)**: Contents, Metadata, Issues, Pull Requests, Members
- **SSO**: Deve ser autorizado para a organização

### Token Clássico
- **Escopos**: `repo`, `read:org`
- **SSO**: Deve ser autorizado para a organização

## Performance e Limitação de Taxa

A ferramenta é projetada para ser amigável aos limites de taxa da API do GitHub:
- Monitoramento automático de limite de taxa e espera
- Contagem configurável de workers para processamento paralelo
- Delays integrados para prevenir abuso da API
- Amostragem inteligente para análise de IA para controlar custos

### Dicas de Otimização
- Use `--only-recent` para análise mais rápida
- Use `--skip-forks` para focar em repositórios originais
- Reduza `--workers` se atingir limites de taxa
- Use `--disable-ai` para execuções mais rápidas sem custos de IA

## Solução de Problemas

### Problemas de Autenticação
```bash
# Teste seu token
curl -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/user

# Depure autenticação
python aval-mds.py --org sua-org --since 2024-01-01 --debug-auth
```

### Problemas Comuns
- **401 Não Autorizado**: Verifique validade do token e autorização SSO
- **Erros de PaginatedList**: Corrigido na v4.0 com iteração segura
- **Resultados vazios**: Verifique intervalo de datas e atividade do repositório
- **Erros de IA**: Verifique chave da API OpenAI e cota

## Arquitetura

### Componentes Principais
- **`AgileQualityAnalyzer`**: Avaliação de qualidade com IA
- **`collect_repo_contrib()`**: Coleta de dados da API do GitHub
- **`build_user_scorer()`**: Implementação do algoritmo de pontuação
- **Limitação de taxa e tratamento de erros**: Interação robusta com API

### Fluxo de Dados
1. **Autenticação**: Verifica acesso ao GitHub e OpenAI
2. **Descoberta de Repositórios**: Encontra repositórios da organização
3. **Coleta de Dados**: Reúne commits, issues, PRs, comentários
4. **Análise de IA**: Avalia qualidade usando OpenAI (opcional)
5. **Pontuação**: Calcula métricas de maturidade ágil
6. **Geração de Saída**: Cria relatório Excel

## Contribuindo

### Configuração de Desenvolvimento
```bash
# Instale dependências de desenvolvimento
pip install -r requirements.txt

# Execute com saída de debug
python aval-mds.py --org org-teste --since 2024-01-01 --debug-auth
```

### Configuração
Pesos de pontuação podem ser ajustados em `CRITERIA_WEIGHTS`:
```python
CRITERIA_WEIGHTS = {
    "weekly_commits": 0.08,
    "ai_commit_quality": 0.08,
    "ai_issue_quality": 0.08,
    # ... outros pesos
}
```

## Licença

Esta ferramenta é projetada para fins educacionais e de pesquisa em engenharia de software e avaliação de metodologia ágil.

## Histórico de Versões

- **v4.4**: Adicionados alertas de frequência de commits (semanas sem atividade)
- **v4.3**: Adicionado suporte para co-authors em commits (Co-authored-by)
- **v4.2**: Adicionada coluna "explicacao_geral" com resumo em linguagem natural da avaliação
- **v4.1**: Adicionado filtro para incluir repositórios criados a partir da data --since
- **v4.0**: Adicionada análise de qualidade com IA usando integração OpenAI
- **v3.2**: Limitação de taxa aprimorada e diagnósticos de autenticação
- **v3.1**: Pesos de critérios melhorados e métricas de estabilidade
- **v3.0**: Processamento multi-thread e pontuação abrangente

## Suporte

Para problemas e questões:
1. Verifique a seção de solução de problemas
2. Verifique as permissões do seu token GitHub
3. Teste com um intervalo de datas menor ou conjunto de usuários
4. Revise a saída de debug com `--debug-auth`
