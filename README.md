# Benfeitorias em Campo

App para conferir e medir benfeitorias rurais em vistoria pericial, a partir de KML/KMZ do Google Earth. Funciona no celular, no tablet e no computador, inclusive sem internet (depois de instalado).

## Começar no Claude Code
```bash
npm ci              # instala o Leaflet
npm run build       # gera dist/
npm run serve       # abre em http://localhost:8080
npm test            # teste ponta a ponta (requer: pip install playwright && playwright install chromium)
```

## Publicar (GitHub Pages)
1. Crie o repositório público `benfeitorias` no GitHub e envie esta pasta (`git init`, `git add .`, `git commit`, `git push`).
2. No repositório: **Settings → Pages → Source: GitHub Actions**.
3. A cada push na `main`, o workflow publica em `https://SEU-USUARIO.github.io/benfeitorias/`.
4. No celular: abra o endereço no Chrome → **⋮ → Adicionar à tela inicial**.

## Passar a perícia do celular para o computador
**Exportar → Backup completo (.json)** no celular → envie o arquivo → no computador, **Restaurar backup**.

Detalhes técnicos em `CLAUDE.md`.
