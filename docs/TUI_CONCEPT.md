# Conceito da TUI — Zer0Specter

## Objetivo

Interface interativa em tela cheia que organiza ferramentas por categoria, adapta-se ao tamanho do terminal e mantém os comandos diretos do CLI disponíveis.

## Navegação e categorias

A navegação combina teclado e campos de texto: setas para mover, Enter para abrir ou executar, Esc para voltar, `/` para buscar e `?` para ajuda. Alvos e opções são digitados em campos próprios; a TUI não funciona como um shell interno.

- **Recon:** port scanner, sniffer e IP geolocation.
- **Web:** OWASP ZAP e sqlmap, disponíveis após a integração do M3.
- **Ofensiva:** Wi-Fi deauth, ZIP cracker e sqlmap.
- **Utilitários:** gerador de senhas.

Uma ferramenta presente em mais de uma categoria é uma referência à mesma ferramenta. Sqlmap aparece em Web e Ofensiva sem duplicar configuração ou resultado.

## Tela ampla

```text
┌─ Zer0Specter ────────────────────────────────────────────────────────────┐
│ TUI   Comandos atuais · M3 planejado                         [?] ajuda  │
├───────────────────┬───────────────────────────────────────────────────┤
│ CATEGORIAS        │ RECON                                             │
│ > Recon           │                                                   │
│   Web             │ Port scanner                                      │
│   Ofensiva        │ Alvo     [127.0.0.1___________________________]    │
│   Utilitários     │ Portas   [1-1024_____________________________]    │
│                   │ Timeout  [1_________________________________]    │
│                   │                                                   │
│                   │ [ Executar ]                                      │
│                   │                                                   │
│                   │ SAÍDA DA EXECUÇÃO                                 │
│                   │ Aguardando execução.                              │
├───────────────────┴───────────────────────────────────────────────────┤
│ ↑↓ navegar  Enter selecionar/executar  Esc voltar  / buscar  q sair   │
└───────────────────────────────────────────────────────────────────────┘
```

## Tela compacta

Em terminais estreitos, as categorias ficam em uma faixa no topo e o painel principal ocupa o restante. Ao abrir uma ferramenta, o formulário substitui a lista de ferramentas; Esc retorna à lista. Campos e resultados rolam verticalmente.

```text
┌─ Zer0Specter · Recon ───┐
│ > Port scanner          │
│   Sniffer               │
│   IP geolocation        │
│                         │
│ ↑↓ mover · Enter abrir  │
└─────────────────────────┘
```

## Tela cheia

A interface usa a área disponível sem dimensões fixas. Em terminais largos, categorias e painel principal ficam lado a lado; abaixo de 96 colunas ou 24 linhas, as categorias ficam acima do painel. A saída usa o espaço restante sem mudar o fluxo principal.

## Fluxo Recon → M3

Ao selecionar um achado, a interface exibe origem e dados associados, e oferece ações compatíveis. O alvo e a requisição seguem para ZAP ou sqlmap sem redigitação. Antes da execução, o operador revisa os dados e escolhe o perfil; ações ativas ficam limitadas ao escopo de laboratório definido pelo M3.

```text
Achado selecionado
Origem: ZAP
Alvo: https://lab.local/item?id=1

Ações
> Abrir no ZAP
  Analisar com sqlmap · leitura
  Analisar com sqlmap · escrita
```

## Estados e apresentação

O painel de saída mostra estado, resumo e saída padronizada do módulo. Erros, interrupções e ferramentas M3 ainda indisponíveis aparecem no mesmo contexto. O visual usa fundo escuro e vermelho para foco e ações; verde fica reservado para sucesso.
