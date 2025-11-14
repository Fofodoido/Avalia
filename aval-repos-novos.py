#!/usr/bin/env python3
# aval-repos-novos.py - v1.0 - Análise de performance ágil de repositórios criados após uma data específica
# Foco: Indicadores de maturidade ágil, análise qualitativa com IA dos artefatos commitados
# Uso: python aval-repos-novos.py --org unb-mds --created-since 2024-08-01 --out repos-analysis.xlsx

import argparse, datetime as dt, re, math, statistics, os, time, sys, json
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from github import Github, GithubException, UnknownObjectException

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[warning] OpenAI not available. Install with: pip install openai")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# ------------------ Configuração de Métricas Ágeis ------------------

AGILE_METRICS_WEIGHTS = {
    "development_velocity": 0.25,        # Velocidade de desenvolvimento
    "collaboration_index": 0.20,         # Índice de colaboração
    "code_quality": 0.20,               # Qualidade do código (IA)
    "documentation_maturity": 0.15,      # Maturidade da documentação (IA)
    "project_structure": 0.10,          # Estrutura do projeto
    "community_engagement": 0.10        # Engajamento da comunidade
}

# ------------------ Análise com IA ------------------

class AgileRepositoryAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        self.enabled = False
        
        if not OPENAI_AVAILABLE:
            return
            
        if api_key or os.getenv("OPENAI_API_KEY"):
            try:
                self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
                self.enabled = True
                print("[ai] OpenAI client initialized for repository analysis")
            except Exception as e:
                print(f"[ai] Failed to initialize OpenAI client: {e}")
    
    def _call_openai(self, messages: List[Dict], max_tokens: int = 200) -> Optional[str]:
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
            print(f"[ai] OpenAI API error: {e}")
            return None
    
    def analyze_commit_quality(self, commit_messages: List[str]) -> Dict:
        if not commit_messages or not self.enabled:
            return {"score": 0.5, "analysis": "Análise não disponível", "recommendations": []}
        
        messages_text = "\n".join([f"- {msg}" for msg in commit_messages[:10]])
        
        prompt_messages = [
            {
                "role": "system",
                "content": "Analise as mensagens de commit para práticas ágeis. "
                          "Forneça: 1) Pontuação 0.0-1.0 2) Análise breve 3) 2 recomendações"
            },
            {
                "role": "user",
                "content": f"Mensagens de commit:\n{messages_text}"
            }
        ]
        
        result = self._call_openai(prompt_messages, max_tokens=200)
        
        if result:
            score_match = re.search(r'(\d+\.?\d*)', result)
            score = float(score_match.group(1)) if score_match else 0.5
            score = max(0.0, min(1.0, score))
            
            return {"score": score, "analysis": result, "recommendations": self._extract_recommendations(result)}
        
        return {"score": 0.5, "analysis": "Análise não disponível", "recommendations": []}
    
    def analyze_project_structure(self, file_structure: List[str], readme_content: str) -> Dict:
        if not self.enabled:
            return {"score": 0.5, "analysis": "Análise não disponível", "recommendations": []}
        
        structure_text = "\n".join(file_structure[:15])
        readme_preview = readme_content[:300] if readme_content else "Sem README"
        
        prompt_messages = [
            {
                "role": "system",
                "content": "Analise estrutura do projeto para práticas ágeis. "
                          "Forneça: 1) Pontuação 0.0-1.0 2) Análise breve 3) 2 recomendações"
            },
            {
                "role": "user",
                "content": f"Estrutura:\n{structure_text}\n\nREADME:\n{readme_preview}"
            }
        ]
        
        result = self._call_openai(prompt_messages, max_tokens=200)
        
        if result:
            score_match = re.search(r'(\d+\.?\d*)', result)
            score = float(score_match.group(1)) if score_match else 0.5
            score = max(0.0, min(1.0, score))
            
            return {"score": score, "analysis": result, "recommendations": self._extract_recommendations(result)}
        
        return {"score": 0.5, "analysis": "Análise não disponível", "recommendations": []}
    
    def _extract_recommendations(self, text: str) -> List[str]:
        recommendations = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recomend', 'sugest', 'melhor', 'deve']):
                clean_line = re.sub(r'^[\d\.\-\*\s]+', '', line).strip()
                if clean_line and len(clean_line) > 10:
                    recommendations.append(clean_line)
        return recommendations[:2]

# ------------------ Coleta de Métricas ------------------

def calculate_development_velocity(repo, created_date: dt.datetime) -> Dict:
    try:
        commits = list(repo.get_commits(since=created_date))
        total_commits = len(commits)
        
        now = dt.datetime.now(dt.timezone.utc)
        weeks_since_creation = max(1, (now - created_date).days / 7)
        velocity = total_commits / weeks_since_creation
        
        return {
            "total_commits": total_commits,
            "weeks_since_creation": round(weeks_since_creation, 1),
            "commits_per_week": round(velocity, 2),
            "score": min(1.0, velocity / 5.0)
        }
    except Exception as e:
        print(f"  Erro ao calcular velocidade: {e}")
        return {"total_commits": 0, "weeks_since_creation": 0, "commits_per_week": 0.0, "score": 0.0}

def calculate_collaboration_index(repo) -> Dict:
    try:
        issues = list(repo.get_issues(state="all"))
        prs = list(repo.get_pulls(state="all"))
        
        unique_contributors = set()
        for issue in issues:
            if issue.user and issue.user.login:
                unique_contributors.add(issue.user.login.lower())
        for pr in prs:
            if pr.user and pr.user.login:
                unique_contributors.add(pr.user.login.lower())
        
        total_issues = len(issues)
        total_prs = len(prs)
        total_contributors = len(unique_contributors)
        
        activity_score = min(1.0, (total_issues + total_prs) / 20.0)
        diversity_score = min(1.0, total_contributors / 5.0)
        collaboration_score = (activity_score + diversity_score) / 2.0
        
        return {
            "total_issues": total_issues,
            "total_prs": total_prs,
            "unique_contributors": total_contributors,
            "score": round(collaboration_score, 3)
        }
    except Exception as e:
        print(f"  Erro ao calcular colaboração: {e}")
        return {"total_issues": 0, "total_prs": 0, "unique_contributors": 0, "score": 0.0}

def analyze_project_structure_metrics(repo) -> Dict:
    try:
        contents = repo.get_contents("")
        file_structure = []
        
        def explore_directory(contents_list, path="", max_depth=2, current_depth=0):
            if current_depth >= max_depth:
                return
            
            for content in contents_list:
                full_path = f"{path}/{content.name}" if path else content.name
                file_structure.append(full_path)
                
                if content.type == "dir" and current_depth < max_depth - 1:
                    try:
                        sub_contents = repo.get_contents(content.path)
                        explore_directory(sub_contents, full_path, max_depth, current_depth + 1)
                    except:
                        pass
        
        explore_directory(contents)
        
        has_readme = any("readme" in f.lower() for f in file_structure)
        has_gitignore = ".gitignore" in file_structure
        has_license = any("license" in f.lower() for f in file_structure)
        has_tests = any("test" in f.lower() for f in file_structure)
        has_ci = any(".github" in f or "ci" in f.lower() for f in file_structure)
        
        structure_elements = [has_readme, has_gitignore, has_license, has_tests, has_ci]
        structure_score = sum(structure_elements) / len(structure_elements)
        
        return {
            "total_files": len(file_structure),
            "has_readme": has_readme,
            "has_tests": has_tests,
            "has_ci": has_ci,
            "file_structure": file_structure[:15],
            "score": round(structure_score, 3)
        }
    except Exception as e:
        print(f"  Erro ao analisar estrutura: {e}")
        return {"total_files": 0, "has_readme": False, "has_tests": False, "has_ci": False, "file_structure": [], "score": 0.0}

def calculate_community_engagement(repo) -> Dict:
    try:
        stars = repo.stargazers_count or 0
        forks = repo.forks_count or 0
        watchers = repo.watchers_count or 0
        
        star_score = min(1.0, stars / 10.0)
        fork_score = min(1.0, forks / 5.0)
        watch_score = min(1.0, watchers / 10.0)
        
        engagement_score = (star_score + fork_score + watch_score) / 3.0
        
        return {
            "stars": stars,
            "forks": forks,
            "watchers": watchers,
            "score": round(engagement_score, 3)
        }
    except Exception as e:
        print(f"  Erro ao calcular engajamento: {e}")
        return {"stars": 0, "forks": 0, "watchers": 0, "score": 0.0}

def analyze_repository_comprehensive(repo, created_since: dt.datetime, ai_analyzer: Optional[AgileRepositoryAnalyzer] = None) -> Dict:
    repo_name = repo.full_name
    created_at = repo.created_at.replace(tzinfo=dt.timezone.utc)
    
    print(f"Analisando: {repo_name}")
    
    velocity_metrics = calculate_development_velocity(repo, created_at)
    collaboration_metrics = calculate_collaboration_index(repo)
    structure_metrics = analyze_project_structure_metrics(repo)
    engagement_metrics = calculate_community_engagement(repo)
    
    # Coleta para IA
    commit_messages = []
    readme_content = ""
    
    try:
        commits = list(repo.get_commits(since=created_since))[:15]
        for commit in commits:
            if commit.commit and commit.commit.message:
                commit_messages.append(commit.commit.message.strip())
        
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode('utf-8')
        except:
            readme_content = ""
    except Exception as e:
        print(f"  Erro ao coletar dados: {e}")
    
    # Análises com IA
    ai_commit_analysis = {"score": 0.5, "analysis": "IA não disponível", "recommendations": []}
    ai_structure_analysis = {"score": 0.5, "analysis": "IA não disponível", "recommendations": []}
    
    if ai_analyzer and ai_analyzer.enabled:
        ai_commit_analysis = ai_analyzer.analyze_commit_quality(commit_messages)
        ai_structure_analysis = ai_analyzer.analyze_project_structure(structure_metrics["file_structure"], readme_content)
    
    # Score final
    final_score = (
        velocity_metrics["score"] * AGILE_METRICS_WEIGHTS["development_velocity"] +
        collaboration_metrics["score"] * AGILE_METRICS_WEIGHTS["collaboration_index"] +
        ai_commit_analysis["score"] * AGILE_METRICS_WEIGHTS["code_quality"] +
        ai_structure_analysis["score"] * AGILE_METRICS_WEIGHTS["documentation_maturity"] +
        structure_metrics["score"] * AGILE_METRICS_WEIGHTS["project_structure"] +
        engagement_metrics["score"] * AGILE_METRICS_WEIGHTS["community_engagement"]
    )
    
    if final_score >= 0.8:
        maturity_level = "Excelente"
    elif final_score >= 0.6:
        maturity_level = "Maduro"
    elif final_score >= 0.4:
        maturity_level = "Em Desenvolvimento"
    else:
        maturity_level = "Iniciante"
    
    return {
        "repo_name": repo_name,
        "created_at": created_at.isoformat(),
        "final_score": round(final_score, 3),
        "maturity_level": maturity_level,
        "velocity_metrics": velocity_metrics,
        "collaboration_metrics": collaboration_metrics,
        "structure_metrics": structure_metrics,
        "engagement_metrics": engagement_metrics,
        "ai_commit_analysis": ai_commit_analysis,
        "ai_structure_analysis": ai_structure_analysis
    }

# ------------------ CLI e Main ------------------

def parse_args():
    ap = argparse.ArgumentParser(description="Análise de performance ágil de repositórios novos")
    ap.add_argument("--org", required=True, help="Organização do GitHub")
    ap.add_argument("--created-since", required=True, help="Data de criação mínima (YYYY-MM-DD)")
    ap.add_argument("--out", default="repos-analysis.xlsx", help="Arquivo XLSX de saída")
    ap.add_argument("--token", default=None, help="GitHub Token (ou via GH_TOKEN env)")
    ap.add_argument("--workers", type=int, default=4, help="Número de workers paralelos")
    ap.add_argument("--openai-key", default=None, help="OpenAI API Key")
    ap.add_argument("--disable-ai", action="store_true", help="Desabilita análise AI")
    return ap.parse_args()

def main():
    args = parse_args()
    
    if DOTENV_AVAILABLE:
        load_dotenv()
    
    token = (args.token or os.getenv("GH_TOKEN", "")).strip()
    gh = Github(token, per_page=50) if token else Github(per_page=50)
    
    ai_analyzer = None
    if not args.disable_ai:
        ai_analyzer = AgileRepositoryAnalyzer(args.openai_key)
    
    created_since = dt.datetime.strptime(args.created_since, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    
    try:
        org = gh.get_organization(args.org)
        print(f"Organização: {org.name}")
    except GithubException as e:
        print(f"Erro: {e}")
        sys.exit(1)
    
    repos_to_analyze = []
    for repo in org.get_repos():
        if repo.created_at.replace(tzinfo=dt.timezone.utc) >= created_since:
            repos_to_analyze.append(repo)
    
    print(f"Repositórios encontrados: {len(repos_to_analyze)}")
    
    if not repos_to_analyze:
        print("Nenhum repositório encontrado.")
        sys.exit(0)
    
    results = []
    
    def analyze_single_repo(repo):
        try:
            return analyze_repository_comprehensive(repo, created_since, ai_analyzer)
        except Exception as e:
            print(f"Erro em {repo.full_name}: {e}")
            return None
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_repo = {executor.submit(analyze_single_repo, repo): repo for repo in repos_to_analyze}
        
        for future in as_completed(future_to_repo):
            result = future.result()
            if result:
                results.append(result)
    
    if results:
        summary_rows = []
        detailed_rows = []
        
        for result in results:
            summary_rows.append({
                "repo_name": result["repo_name"],
                "created_at": result["created_at"],
                "final_score": result["final_score"],
                "maturity_level": result["maturity_level"],
                "commits_per_week": result["velocity_metrics"]["commits_per_week"],
                "total_contributors": result["collaboration_metrics"]["unique_contributors"],
                "total_issues": result["collaboration_metrics"]["total_issues"],
                "total_prs": result["collaboration_metrics"]["total_prs"],
                "has_readme": result["structure_metrics"]["has_readme"],
                "has_tests": result["structure_metrics"]["has_tests"],
                "stars": result["engagement_metrics"]["stars"],
                "ai_commit_score": result["ai_commit_analysis"]["score"],
                "ai_structure_score": result["ai_structure_analysis"]["score"]
            })
            
            detailed_rows.append({
                "repo_name": result["repo_name"],
                "final_score": result["final_score"],
                "maturity_level": result["maturity_level"],
                "ai_commit_analysis": result["ai_commit_analysis"]["analysis"],
                "ai_structure_analysis": result["ai_structure_analysis"]["analysis"],
                "commit_recommendations": "; ".join(result["ai_commit_analysis"]["recommendations"]),
                "structure_recommendations": "; ".join(result["ai_structure_analysis"]["recommendations"])
            })
        
        summary_df = pd.DataFrame(summary_rows).sort_values("final_score", ascending=False)
        detailed_df = pd.DataFrame(detailed_rows).sort_values("final_score", ascending=False)
        
        metadata_df = pd.DataFrame([{
            "org": args.org,
            "created_since": args.created_since,
            "total_repos": len(results),
            "generated_at": dt.datetime.now().isoformat(),
            "script_version": "aval-repos-novos.py v1.0"
        }])
        
        with pd.ExcelWriter(args.out, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Resumo_Repositorios', index=False)
            detailed_df.to_excel(writer, sheet_name='Analises_Detalhadas', index=False)
            metadata_df.to_excel(writer, sheet_name='Metadados', index=False)
        
        print(f"\nConcluído! Arquivo: {args.out}")
        print(f"Repositórios analisados: {len(results)}")
        print(f"Score médio: {summary_df['final_score'].mean():.3f}")

if __name__ == "__main__":
    main()
