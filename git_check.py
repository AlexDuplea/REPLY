#!/usr/bin/env python3
"""
Git Safety Check - Verifica che non vengano committati file sensibili
"""

import os
import subprocess
import sys

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_command(cmd):
    """Esegue comando e ritorna output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return ""

def check_git_initialized():
    """Verifica che git sia inizializzato"""
    if not os.path.exists('.git'):
        print(f"{Colors.YELLOW}⚠️  Repository Git non inizializzato{Colors.ENDC}")
        print("\nEsegui: git init")
        return False
    return True

def check_sensitive_files():
    """Controlla che file sensibili non siano tracciati"""
    print(f"\n{Colors.BOLD}🔒 Controllo File Sensibili{Colors.ENDC}")
    print("=" * 60)
    
    sensitive_files = ['.env', 'data/']
    issues = []
    
    # File tracciati da git
    tracked_files = run_command("git ls-files").split('\n')
    
    for sensitive in sensitive_files:
        for tracked in tracked_files:
            if tracked.startswith(sensitive) or tracked == sensitive:
                issues.append(tracked)
    
    if issues:
        print(f"{Colors.RED}❌ ATTENZIONE! File sensibili tracciati:{Colors.ENDC}")
        for f in issues:
            print(f"   - {f}")
        print(f"\n{Colors.YELLOW}Rimuovili con:{Colors.ENDC}")
        for f in issues:
            print(f"   git rm --cached {f}")
        return False
    else:
        print(f"{Colors.GREEN}✅ Nessun file sensibile tracciato{Colors.ENDC}")
        return True

def check_staged_files():
    """Mostra file in staging"""
    print(f"\n{Colors.BOLD}📋 File in Staging{Colors.ENDC}")
    print("=" * 60)
    
    staged = run_command("git diff --cached --name-only")
    
    if not staged:
        print(f"{Colors.YELLOW}Nessun file in staging{Colors.ENDC}")
        print("\nEsegui: git add . (dopo aver verificato)")
        return False
    
    files = staged.split('\n')
    print(f"{Colors.GREEN}File pronti per commit:{Colors.ENDC}")
    for f in files:
        if f:
            print(f"   ✓ {f}")
    
    return True

def check_gitignore():
    """Verifica che .gitignore sia corretto"""
    print(f"\n{Colors.BOLD}📝 Verifica .gitignore{Colors.ENDC}")
    print("=" * 60)
    
    if not os.path.exists('.gitignore'):
        print(f"{Colors.RED}❌ .gitignore mancante!{Colors.ENDC}")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    required = ['.env', 'data/', '__pycache__']
    missing = []
    
    for req in required:
        if req not in content:
            missing.append(req)
    
    if missing:
        print(f"{Colors.YELLOW}⚠️  Mancano in .gitignore:{Colors.ENDC}")
        for m in missing:
            print(f"   - {m}")
        return False
    else:
        print(f"{Colors.GREEN}✅ .gitignore configurato correttamente{Colors.ENDC}")
        return True

def check_env_example():
    """Verifica che .env.example esista"""
    print(f"\n{Colors.BOLD}🔑 Verifica .env.example{Colors.ENDC}")
    print("=" * 60)
    
    if not os.path.exists('.env.example'):
        print(f"{Colors.YELLOW}⚠️  .env.example mancante{Colors.ENDC}")
        print("Consigliato per documentare le variabili necessarie")
        return False
    
    print(f"{Colors.GREEN}✅ .env.example presente{Colors.ENDC}")
    return True

def suggest_next_steps(all_good):
    """Suggerisce prossimi passi"""
    print(f"\n{Colors.BOLD}📌 Prossimi Passi{Colors.ENDC}")
    print("=" * 60 + "\n")
    
    if all_good:
        print(f"{Colors.GREEN}✅ Tutto pronto per il commit!{Colors.ENDC}\n")
        print("Comandi suggeriti:")
        print(f"{Colors.BLUE}git commit -m \"feat: initial commit\"{Colors.ENDC}")
        print(f"{Colors.BLUE}git branch -M main{Colors.ENDC}")
        print(f"{Colors.BLUE}git remote add origin https://github.com/USERNAME/REPO.git{Colors.ENDC}")
        print(f"{Colors.BLUE}git push -u origin main{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Risolvi i problemi sopra prima del commit{Colors.ENDC}")

def main():
    print("=" * 60)
    print(f"{Colors.BOLD}GIT SAFETY CHECK - Mental Wellness Journal{Colors.ENDC}")
    print("=" * 60)
    
    if not check_git_initialized():
        return
    
    checks = [
        check_gitignore(),
        check_env_example(),
        check_sensitive_files(),
        check_staged_files()
    ]
    
    all_good = all(checks)
    
    suggest_next_steps(all_good)
    
    print("\n" + "=" * 60 + "\n")
    
    if not all_good:
        sys.exit(1)

if __name__ == "__main__":
    main()
