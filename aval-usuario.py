#!/usr/bin/env python3
# aval-usuario.py - v1.1 - Análise detalhada de um usuário em um repositório específico + alertas de frequência
# Uso: python aval-usuario.py --repo owner/repo --user username --since 2024-08-01

import argparse, datetime as dt, re, math, statistics, os, time, sys, json
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from github import Github, GithubException, UnknownObjectException

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[warning] OpenAI não disponível. Instale com: pip install openai")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("[warning] python-dotenv não disponível. Instale com: pip install python-dotenv")

# ------------------ Configurações ------------------

SAMPLE_SIZE = 20  # Mais amostras para análise detalhada
MAX_FILES_GOOD = 10
MIN_MSG_LEN = 8

class DetailedAgileAnalyzer:
    """Analisador detalhado de práticas ágeis para um usuário específico."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        self.enabled = False
        
        if not OPENAI_AVAILABLE:
            return
            
        if api_key or os.getenv("OPENAI_API_KEY"):
            try:
                self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
                self.client.models.list()
                self.enabled = True
                print("[ai] Cliente OpenAI inicializado com sucesso")
            except Exception as e:
                print(f"[ai] Falha ao inicializar cliente OpenAI: {e}")
    
    def _call_openai(self, messages: List[Dict], max_tokens: int = 200) -> Optional[str]:
        """Chamada segura para API OpenAI."""
        if not self.enabled:
            return None
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,
                timeout=15
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ai] Erro na API OpenAI: {e}")
            return None
    
    def analyze_commits_detailed(self, commits_data: List[Dict]) -> Dict:
        """Análise detalhada de commits com IA."""
        if not commits_data:
            return {"score": 0.5, "analysis": "Nenhum commit encontrado", "recommendations": []}
        
        # Extrair mensagens
        messages = [c["message"] for c in commits_data if c["message"]]
        
        if not self.enabled or not messages:
            return {
                "score": 0.5, 
                "analysis": f"Análise básica: {len(messages)} commits encontrados",
                "recommendations": ["Configure OpenAI para análise detalhada"]
            }
        
        # Análise com IA
        messages_text = "\n".join([f"- {msg}" for msg in messages[:10]])
        
        prompt_messages = [
            {
                "role": "system",
                "content": "Você é um especialista em práticas ágeis e qualidade de commits. "
                          "Analise as mensagens de commit e forneça: "
                          "1) Uma pontuação de 0.0 a 1.0 "
                          "2) Análise detalhada dos pontos fortes e fracos "
                          "3) 3 recomendações específicas para melhoria"
            },
            {
                "role": "user",
                "content": f"Analise estas mensagens de commit:\n{messages_text}"
            }
        ]
        
        result = self._call_openai(prompt_messages, max_tokens=300)
        
        if result:
            # Extrair pontuação
            score_match = re.search(r'(\d+\.?\d*)', result)
            score = float(score_match.group(1)) if score_match else 0.5
            score = max(0.0, min(1.0, score))
            
            # Extrair recomendações
            recommendations = []
            lines = result.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['recomend', 'sugest', 'melhor', 'deve']):
                    recommendations.append(line.strip('- ').strip())
            
            return {
                "score": score,
                "analysis": result,
                "recommendations": recommendations[:3] if recommendations else [
                    "Melhore a clareza das mensagens de commit",
                    "Use formato convencional (feat:, fix:, docs:)",
                    "Descreva o 'porquê' além do 'o quê'"
                ]
            }
        
        return {"score": 0.5, "analysis": "Falha na análise de IA", "recommendations": []}
    
    def analyze_issues_detailed(self, issues_data: List[Dict]) -> Dict:
        """Análise detalhada de issues com IA."""
        if not issues_data:
            return {"score": 0.5, "analysis": "Nenhuma issue encontrada", "recommendations": []}
        
        if not self.enabled:
            return {
                "score": 0.5,
                "analysis": f"Análise básica: {len(issues_data)} issues encontradas",
                "recommendations": ["Configure OpenAI para análise detalhada"]
            }
        
        # Preparar texto das issues
        issues_text = "\n---\n".join([
            f"Título: {issue['title']}\nDescrição: {issue['body'][:500]}..."
            for issue in issues_data[:5]
        ])
        
        prompt_messages = [
            {
                "role": "system",
                "content": "Você é um especialista em histórias de usuário ágeis. "
                          "Analise as issues e forneça: "
                          "1) Pontuação de 0.0 a 1.0 "
                          "2) Análise da qualidade das histórias "
                          "3) Recomendações específicas"
            },
            {
                "role": "user",
                "content": f"Analise estas issues/histórias:\n{issues_text}"
            }
        ]
        
        result = self._call_openai(prompt_messages, max_tokens=300)
        
        if result:
            score_match = re.search(r'(\d+\.?\d*)', result)
            score = float(score_match.group(1)) if score_match else 0.5
            score = max(0.0, min(1.0, score))
            
            recommendations = []
            lines = result.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['recomend', 'sugest', 'melhor', 'deve']):
                    recommendations.append(line.strip('- ').strip())
            
            return {
                "score": score,
                "analysis": result,
                "recommendations": recommendations[:3] if recommendations else [
                    "Adicione critérios de aceitação claros",
                    "Use formato 'Como... Eu quero... Para que...'",
                    "Inclua mais detalhes técnicos"
                ]
            }
        
        return {"score": 0.5, "analysis": "Falha na análise de IA", "recommendations": []}
    
    def analyze_reviews_detailed(self, reviews_data: List[Dict]) -> Dict:
        """Análise detalhada de revisões com IA."""
        if not reviews_data:
            return {"score": 0.5, "analysis": "Nenhuma revisão encontrada", "recommendations": []}
        
        if not self.enabled:
            return {
                "score": 0.5,
                "analysis": f"Análise básica: {len(reviews_data)} revisões encontradas",
                "recommendations": ["Configure OpenAI para análise detalhada"]
            }
        
        # Preparar texto das revisões
        reviews_text = "\n".join([
            f"- {review['body'][:200]}..."
            for review in reviews_data[:8] if review['body']
        ])
        
        prompt_messages = [
            {
                "role": "system",
                "content": "Você é um especialista em revisão de código. "
                          "Analise os comentários de revisão e forneça: "
                          "1) Pontuação de 0.0 a 1.0 "
                          "2) Análise da qualidade das revisões "
                          "3) Recomendações para melhorar"
            },
            {
                "role": "user",
                "content": f"Analise estes comentários de revisão:\n{reviews_text}"
            }
        ]
        
        result = self._call_openai(prompt_messages, max_tokens=300)
        
        if result:
            score_match = re.search(r'(\d+\.?\d*)', result)
            score = float(score_match.group(1)) if score_match else 0.5
            score = max(0.0, min(1.0, score))
            
            recommendations = []
            lines = result.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['recomend', 'sugest', 'melhor', 'deve']):
                    recommendations.append(line.strip('- ').strip())
            
            return {
                "score": score,
                "analysis": result,
                "recommendations": recommendations[:3] if recommendations else [
                    "Forneça feedback mais específico",
                    "Sugira melhorias construtivas",
                    "Foque em qualidade, segurança e performance"
                ]
            }
        
        return {"score": 0.5, "analysis": "Falha na análise de IA", "recommendations": []}

def collect_user_data(repo, username: str, since_dt: dt.datetime) -> Dict:
    """Coleta dados detalhados de um usuário específico."""
    print(f"Coletando dados de {username} no repositório {repo.full_name}...")
    
    data = {
        "commits": [],
        "issues": [],
        "prs": [],
        "reviews": [],
        "stats": {
            "commits_count": 0,
            "issues_count": 0,
            "prs_count": 0,
            "reviews_count": 0,
            "lines_added": 0,
            "lines_removed": 0,
            "files_changed": 0
        }
    }
    
    # Coletar commits
    print("  Coletando commits...")
    try:
        for commit in repo.get_commits(author=username, since=since_dt):
            if not commit.commit or not commit.commit.author:
                continue
                
            commit_data = {
                "sha": commit.sha,
                "message": commit.commit.message,
                "date": commit.commit.author.date,
                "files_count": 0,
                "additions": 0,
                "deletions": 0
            }
            
            try:
                files = getattr(commit, "files", None) or []
                commit_data["files_count"] = sum(1 for _ in files)
                
                stats = getattr(commit, "stats", None)
                if stats:
                    commit_data["additions"] = getattr(stats, "additions", 0)
                    commit_data["deletions"] = getattr(stats, "deletions", 0)
                    data["stats"]["lines_added"] += commit_data["additions"]
                    data["stats"]["lines_removed"] += commit_data["deletions"]
                    data["stats"]["files_changed"] += commit_data["files_count"]
            except:
                pass
            
            data["commits"].append(commit_data)
            data["stats"]["commits_count"] += 1
            
            if len(data["commits"]) >= SAMPLE_SIZE:
                break
                
    except GithubException as e:
        print(f"  Erro ao coletar commits: {e}")
    
    # Coletar issues
    print("  Coletando issues...")
    try:
        for issue in repo.get_issues(creator=username, state="all", since=since_dt):
            if issue.pull_request is None:  # Apenas issues, não PRs
                issue_data = {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body or "",
                    "state": issue.state,
                    "created_at": issue.created_at,
                    "comments_count": issue.comments,
                    "labels": [label.name for label in issue.labels]
                }
                
                data["issues"].append(issue_data)
                data["stats"]["issues_count"] += 1
                
                if len(data["issues"]) >= SAMPLE_SIZE:
                    break
    except GithubException as e:
        print(f"  Erro ao coletar issues: {e}")
    
    # Coletar PRs
    print("  Coletando pull requests...")
    try:
        for pr in repo.get_pulls(state="all", sort="created", direction="desc"):
            if pr.user and pr.user.login.lower() == username.lower():
                pr_data = {
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body or "",
                    "state": pr.state,
                    "created_at": pr.created_at,
                    "merged": pr.merged,
                    "comments_count": pr.comments,
                    "review_comments_count": pr.review_comments,
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                    "changed_files": pr.changed_files
                }
                
                data["prs"].append(pr_data)
                data["stats"]["prs_count"] += 1
                
                if len(data["prs"]) >= SAMPLE_SIZE:
                    break
    except GithubException as e:
        print(f"  Erro ao coletar PRs: {e}")
    
    # Coletar comentários de revisão
    print("  Coletando comentários de revisão...")
    try:
        for pr in repo.get_pulls(state="all", sort="created", direction="desc"):
            try:
                # Comentários gerais do PR
                for comment in pr.get_issue_comments():
                    if comment.user and comment.user.login.lower() == username.lower():
                        data["reviews"].append({
                            "type": "pr_comment",
                            "body": comment.body,
                            "created_at": comment.created_at,
                            "pr_number": pr.number
                        })
                        data["stats"]["reviews_count"] += 1
                
                # Comentários de revisão de código
                for comment in pr.get_review_comments():
                    if comment.user and comment.user.login.lower() == username.lower():
                        data["reviews"].append({
                            "type": "review_comment",
                            "body": comment.body,
                            "created_at": comment.created_at,
                            "pr_number": pr.number,
                            "path": getattr(comment, "path", "")
                        })
                        data["stats"]["reviews_count"] += 1
                
                if len(data["reviews"]) >= SAMPLE_SIZE:
                    break
                    
            except GithubException:
                continue
                
    except GithubException as e:
        print(f"  Erro ao coletar revisões: {e}")
    
    print(f"Coleta concluída: {data['stats']['commits_count']} commits, "
          f"{data['stats']['issues_count']} issues, {data['stats']['prs_count']} PRs, "
          f"{data['stats']['reviews_count']} revisões")
    
    return data

def analyze_commit_frequency(commits_data: List[Dict], since_date: str) -> Dict:
    """Analisa frequência de commits e identifica períodos de inatividade."""
    if not commits_data:
        return {
            "commits_per_week": 0.0,
            "weeks_inactive": 0,
            "frequency_alert": "Nenhum commit encontrado no período",
            "alert_level": "critical"
        }
    
    # Calcular período em semanas
    import datetime as dt
    since_dt = dt.datetime.strptime(since_date, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    now_dt = dt.datetime.now(dt.timezone.utc)
    weeks_in_period = max(1, (now_dt - since_dt).days // 7)
    
    commits_total = len(commits_data)
    commits_per_week = commits_total / weeks_in_period
    
    # Estimar semanas sem commits
    if commits_total == 0:
        weeks_inactive = weeks_in_period
        alert_level = "critical"
        frequency_alert = f"CRÍTICO: {weeks_in_period} semanas sem nenhum commit"
    else:
        weeks_inactive = max(0, weeks_in_period - commits_total)
        
        if commits_per_week < 1.0:
            if weeks_inactive >= weeks_in_period * 0.7:
                alert_level = "high"
                frequency_alert = f"ALERTA: ~{weeks_inactive:.0f} semanas inativas de {weeks_in_period} semanas"
            elif weeks_inactive >= weeks_in_period * 0.4:
                alert_level = "medium"
                frequency_alert = f"Atenção: ~{weeks_inactive:.0f} semanas com baixa atividade de {weeks_in_period} semanas"
            elif commits_per_week < 0.5:
                alert_level = "low"
                frequency_alert = f"Frequência baixa: {commits_per_week:.1f} commits/semana"
            else:
                alert_level = "normal"
                frequency_alert = f"Frequência adequada: {commits_per_week:.1f} commits/semana"
        else:
            alert_level = "good"
            frequency_alert = f"Boa frequência: {commits_per_week:.1f} commits/semana"
    
    return {
        "commits_per_week": round(commits_per_week, 2),
        "weeks_inactive": int(weeks_inactive),
        "weeks_total": weeks_in_period,
        "frequency_alert": frequency_alert,
        "alert_level": alert_level
    }

def generate_detailed_report(username: str, repo_name: str, data: Dict, ai_analysis: Dict, since_date: str) -> str:
    """Gera relatório detalhado em markdown."""
    
    # Análise de frequência de commits
    frequency_analysis = analyze_commit_frequency(data['commits'], since_date)
    
    # Definir emoji baseado no nível de alerta
    alert_emoji = {
        "critical": "🚨",
        "high": "⚠️", 
        "medium": "⚠️",
        "low": "📊",
        "normal": "✅",
        "good": "🎯"
    }.get(frequency_analysis['alert_level'], "📊")
    
    report = f"""# Relatório Detalhado de Práticas Ágeis

**Usuário:** {username}  
**Repositório:** {repo_name}  
**Período:** Desde {since_date}  
**Gerado em:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Resumo Executivo

### Estatísticas Gerais
- **Commits:** {data['stats']['commits_count']}
- **Issues:** {data['stats']['issues_count']}
- **Pull Requests:** {data['stats']['prs_count']}
- **Comentários de Revisão:** {data['stats']['reviews_count']}
- **Linhas Adicionadas:** {data['stats']['lines_added']:,}
- **Linhas Removidas:** {data['stats']['lines_removed']:,}
- **Arquivos Modificados:** {data['stats']['files_changed']}

### Análise de Frequência de Commits
{alert_emoji} **{frequency_analysis['frequency_alert']}**
- **Commits por Semana:** {frequency_analysis['commits_per_week']}
- **Semanas no Período:** {frequency_analysis['weeks_total']}
- **Semanas Estimadas Inativas:** {frequency_analysis['weeks_inactive']}

### Pontuações de Qualidade (IA)
- **Qualidade de Commits:** {ai_analysis['commits']['score']:.2f}/1.0
- **Qualidade de Issues:** {ai_analysis['issues']['score']:.2f}/1.0
- **Qualidade de Revisões:** {ai_analysis['reviews']['score']:.2f}/1.0

---

## Análise de Commits

### Pontuação: {ai_analysis['commits']['score']:.2f}/1.0

{ai_analysis['commits']['analysis']}

### Recomendações para Commits:
"""
    
    for i, rec in enumerate(ai_analysis['commits']['recommendations'], 1):
        report += f"{i}. {rec}\n"
    
    report += f"""
### Últimos Commits:
"""
    
    for commit in data['commits'][:5]:
        report += f"- **{commit['date'].strftime('%Y-%m-%d')}**: {commit['message'][:100]}...\n"
    
    report += f"""
---

## Análise de Issues

### Pontuação: {ai_analysis['issues']['score']:.2f}/1.0

{ai_analysis['issues']['analysis']}

### Recomendações para Issues:
"""
    
    for i, rec in enumerate(ai_analysis['issues']['recommendations'], 1):
        report += f"{i}. {rec}\n"
    
    report += f"""
### Issues Recentes:
"""
    
    for issue in data['issues'][:5]:
        report += f"- **#{issue['number']}** ({issue['state']}): {issue['title']}\n"
    
    report += f"""
---

## Análise de Pull Requests

### Estatísticas de PRs:
- **Total:** {data['stats']['prs_count']}
- **Média de Adições por PR:** {(data['stats']['lines_added'] / max(1, data['stats']['prs_count'])):.1f}
- **Média de Arquivos por PR:** {(data['stats']['files_changed'] / max(1, data['stats']['prs_count'])):.1f}

### PRs Recentes:
"""
    
    for pr in data['prs'][:5]:
        status = "Merged" if pr['merged'] else f"{pr['state'].title()}"
        report += f"- **#{pr['number']}** ({status}): {pr['title']}\n"
    
    report += f"""
---

## Análise de Revisões de Código

### Pontuação: {ai_analysis['reviews']['score']:.2f}/1.0

{ai_analysis['reviews']['analysis']}

### Recomendações para Revisões:
"""
    
    for i, rec in enumerate(ai_analysis['reviews']['recommendations'], 1):
        report += f"{i}. {rec}\n"
    
    report += f"""
---

## Recomendações Gerais

### Pontos Fortes Identificados:
- Atividade consistente no repositório
- Participação em diferentes aspectos do desenvolvimento
- Engajamento com a equipe através de revisões

### Áreas de Melhoria:
1. **Commits:** Foque em mensagens mais descritivas e atômicas
2. **Issues:** Melhore a estruturação das histórias de usuário
3. **Revisões:** Forneça feedback mais específico e construtivo

### Próximos Passos:
1. Implemente as recomendações específicas de cada área
2. Monitore o progresso mensalmente
3. Busque feedback da equipe sobre melhorias implementadas

---

## Análise de Frequência e Consistência

### Status de Frequência:
{alert_emoji} **{frequency_analysis['frequency_alert']}**

### Métricas de Consistência:
- **Frequência Real:** {frequency_analysis['commits_per_week']} commits/semana
- **Período Analisado:** {frequency_analysis['weeks_total']} semanas
- **Semanas Inativas (estimativa):** {frequency_analysis['weeks_inactive']} semanas
- **Taxa de Atividade:** {((frequency_analysis['weeks_total'] - frequency_analysis['weeks_inactive']) / frequency_analysis['weeks_total'] * 100):.1f}%

### Recomendações de Frequência:"""
    
    # Adicionar recomendações baseadas no nível de alerta
    frequency_recommendations = {
        "critical": [
            "🚨 URGENTE: Estabeleça uma rotina de commits diária",
            "📅 Defina metas semanais mínimas de commits",
            "🤝 Considere pair programming para aumentar atividade"
        ],
        "high": [
            "⚠️ Melhore a consistência com commits mais frequentes",
            "📊 Estabeleça uma meta de pelo menos 1 commit por semana",
            "🔄 Revise seu workflow de desenvolvimento"
        ],
        "medium": [
            "📈 Aumente gradualmente a frequência de commits",
            "⏰ Considere commits menores e mais frequentes",
            "📝 Documente melhor seu progresso diário"
        ],
        "low": [
            "✅ Mantenha a frequência atual",
            "🎯 Considere commits ainda mais frequentes para melhor rastreamento",
            "📊 Continue monitorando sua consistência"
        ],
        "normal": [
            "✅ Boa frequência de commits",
            "🎯 Mantenha a consistência atual",
            "📈 Considere pequenos ajustes para otimizar"
        ],
        "good": [
            "🎯 Excelente frequência de commits!",
            "✅ Continue com a consistência atual",
            "🌟 Sirva de exemplo para outros desenvolvedores"
        ]
    }
    
    for i, rec in enumerate(frequency_recommendations.get(frequency_analysis['alert_level'], []), 1):
        report += f"\n{i}. {rec}"
    
    report += f"""

---

## Métricas de Produtividade

### Atividade por Tipo:
- **Commits/Semana:** {frequency_analysis['commits_per_week']}
- **Issues/Mês:** {(data['stats']['issues_count'] / max(1, frequency_analysis['weeks_total'] / 4)):.1f}
- **PRs/Mês:** {(data['stats']['prs_count'] / max(1, frequency_analysis['weeks_total'] / 4)):.1f}
- **Revisões/Mês:** {(data['stats']['reviews_count'] / max(1, frequency_analysis['weeks_total'] / 4)):.1f}

### Impacto no Código:
- **Razão Adição/Remoção:** {(data['stats']['lines_added'] / max(1, data['stats']['lines_removed'])):.2f}
- **Linhas por Commit:** {(data['stats']['lines_added'] / max(1, data['stats']['commits_count'])):.1f}

---

*Relatório gerado pela ferramenta de Avaliação de Práticas Ágeis v1.1*
"""
    
    return report

def parse_args():
    ap = argparse.ArgumentParser(description="Análise detalhada de práticas ágeis para um usuário específico")
    ap.add_argument("--repo", required=True, help="Repositório no formato owner/repo")
    ap.add_argument("--user", required=True, help="Username do GitHub para analisar")
    ap.add_argument("--since", required=True, help="Data de início (YYYY-MM-DD)")
    ap.add_argument("--token", default=None, help="GitHub Token (ou via GH_TOKEN env)")
    ap.add_argument("--openai-key", default=None, help="OpenAI API Key (ou via OPENAI_API_KEY env)")
    ap.add_argument("--disable-ai", action="store_true", help="Desabilitar análise de IA")
    ap.add_argument("--out", default=None, help="Arquivo de saída (padrão: user-repo-analysis.md)")
    return ap.parse_args()

def main():
    args = parse_args()
    
    # Carregar .env se disponível
    if DOTENV_AVAILABLE:
        load_dotenv()
    
    # Configurar tokens
    token = (args.token or os.getenv("GH_TOKEN", "")).strip()
    if not token:
        print("Token do GitHub é obrigatório. Configure GH_TOKEN ou use --token")
        sys.exit(1)
    
    # Inicializar GitHub
    gh = Github(token, per_page=100)
    
    # Verificar autenticação
    try:
        user = gh.get_user()
        print(f"Autenticado como: {user.login}")
    except GithubException as e:
        print(f"Erro de autenticação: {e}")
        sys.exit(1)
    
    # Obter repositório
    try:
        repo = gh.get_repo(args.repo)
        print(f"Repositório encontrado: {repo.full_name}")
    except GithubException as e:
        print(f"Erro ao acessar repositório {args.repo}: {e}")
        sys.exit(1)
    
    # Configurar datas
    since_dt = dt.datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    
    # Inicializar analisador de IA
    ai_analyzer = None
    if not args.disable_ai:
        ai_analyzer = DetailedAgileAnalyzer(args.openai_key)
    
    # Coletar dados
    data = collect_user_data(repo, args.user, since_dt)
    
    # Análise com IA
    print("Executando análise de IA...")
    ai_analysis = {
        "commits": ai_analyzer.analyze_commits_detailed(data["commits"]) if ai_analyzer else {"score": 0.5, "analysis": "IA desabilitada", "recommendations": []},
        "issues": ai_analyzer.analyze_issues_detailed(data["issues"]) if ai_analyzer else {"score": 0.5, "analysis": "IA desabilitada", "recommendations": []},
        "reviews": ai_analyzer.analyze_reviews_detailed(data["reviews"]) if ai_analyzer else {"score": 0.5, "analysis": "IA desabilitada", "recommendations": []}
    }
    
    # Gerar relatório
    print("Gerando relatório...")
    report = generate_detailed_report(args.user, args.repo, data, ai_analysis, args.since)
    
    # Salvar arquivo
    output_file = args.out or f"{args.user}-{args.repo.replace('/', '-')}-analysis.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Relatório salvo em: {output_file}")
    
    # Resumo final
    print(f"""
Análise Concluída!

Resumo:
- Commits: {data['stats']['commits_count']}
- Issues: {data['stats']['issues_count']} 
- PRs: {data['stats']['prs_count']}
- Revisões: {data['stats']['reviews_count']}

Pontuações IA:
- Commits: {ai_analysis['commits']['score']:.2f}/1.0
- Issues: {ai_analysis['issues']['score']:.2f}/1.0
- Revisões: {ai_analysis['reviews']['score']:.2f}/1.0

Relatório detalhado: {output_file}
""")

if __name__ == "__main__":
    main()
