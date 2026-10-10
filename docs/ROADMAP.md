# Roadmap Zer0Specter

## M1 — Padronização das saídas dos módulos

**Status: Concluído**

Padronizar as saídas dos cores atuais em `modules`.

## M2 — TUI

**Status: Concluído**

Criar a TUI em tela cheia integrada ao CLI direto, com categorias, formulários para as ferramentas atuais, execução em subprocesso sem shell e adaptação a terminais compactos e amplos. ZAP e sqlmap continuam identificados como planejados para M3.

### Entregue

- Abrir a interface com `zer0specter tui`, preservando ajuda e comandos diretos.
- Organizar Recon, Web, Ofensiva e Utilitários; sqlmap é listado em Web e Ofensiva, mas permanece indisponível até M3.
- Encaminhar argumentos como tokens separados e exibir `stdout`, `stderr`, código de saída e cancelamento na interface.
- Reorganizar o layout abaixo de 96 colunas ou 24 linhas e usar o espaço disponível em terminais maiores.
- Exigir Python 3.9+ e incluir Textual nas dependências do projeto.
- Verificar comportamento e layout em testes automatizados e em PTY.

## M3 — Integrações web e fluxo recon→ação

**Status: Planejado**

Integrar ferramentas web existentes e conectar achados de reconhecimento a ações subsequentes, sem copiar e colar dados. O fluxo deverá funcionar pela TUI e pelos comandos diretos do CLI.

### Escopo

- Criar adaptadores enxutos para OWASP ZAP e sqlmap; não criar um framework genérico de plugins nem alterar os módulos existentes.
- Permitir perfis passivo e ativo do ZAP e escolher um perfil de leitura ou escrita por execução de SQLi.
- Permitir selecionar um achado e reaproveitar os dados da requisição na ferramenta seguinte.
- Restringir ações a localhost, containers ou CIDRs privados declarados explicitamente. Fluxos de RCE e callback devem ficar limitados a esses alvos.
- Produzir JSON normalizado junto da saída original da ferramenta. Manter artefatos potencialmente sensíveis em local privado e fora dos logs.
- Detectar a distribuição Linux por `/etc/os-release` e exibir instruções para ferramentas ausentes, sem instalá-las automaticamente.

### Verificação prevista

- Cobrir encaminhamento de achados e requisições, perfis de execução, validação de escopo, ferramentas ausentes e proteção dos artefatos.
- Executar testes de integração em laboratório local controlado, pelos caminhos de CLI e TUI.
