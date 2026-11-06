#!/usr/bin/env node
// Gerador de documentos Word (.docx) da Fábrica.
// Converte o Markdown produzido pela CLI (títulos, parágrafos, listas, tabelas, citações, código)
// num documento com capa, cabeçalho, rodapé com "Página X de Y" e tabelas formatadas.
//
// Uso: node fabrica/ferramentas/word.cjs <entrada.md> <saida.docx> [meta.json]
//   meta: {titulo, subtitulo, orgao, contrato, periodo, gerado_em, classificacao, sem_capa,
//          timbrado: {imagem, numero, data, empresa, local, assinatura: {nome, cargo}},
//          assinaturas: [{nome, cargo, entidade}] (dois ou mais blocos lado a lado; nome vazio = linha para preencher)}
//   Com "timbrado", cada página usa o papel timbrado da empresa como fundo (tema escuro e dourado).
//   Imagens no Markdown: ![legenda](caminho.png) — caminho relativo ao arquivo .md.
"use strict";
const fs = require("fs");
const path = require("path");
let docx;
try {
  docx = require("docx");
} catch (e) {
  try {
    docx = require(path.join(__dirname, "node_modules", "docx"));
  } catch (e2) {
    console.error("Biblioteca 'docx' ausente. Instale com: npm install --prefix fabrica/ferramentas");
    process.exit(3);
  }
}
const {
  AlignmentType, BorderStyle, Document, Footer, Header, HeadingLevel, LevelFormat, PageBreak, PageNumber,
  Packer, Paragraph, ShadingType, Table, TableCell, TableRow, TextRun, WidthType, VerticalAlign,
  ImageRun, HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom, TextWrappingType,
} = docx;

const [entrada, saida, metaArq] = process.argv.slice(2);
if (!entrada || !saida) { console.error("uso: word.cjs <entrada.md> <saida.docx> [meta.json]"); process.exit(2); }
const meta = metaArq ? JSON.parse(fs.readFileSync(metaArq, "utf8")) : {};
const linhas = fs.readFileSync(entrada, "utf8").replace(/\r/g, "").split("\n");

const TIMBRADO = meta.timbrado && meta.timbrado.imagem && fs.existsSync(meta.timbrado.imagem) ? meta.timbrado : null;
const BASE_MD = path.dirname(path.resolve(entrada));

// Paleta: institucional (azul) ou papel timbrado (preto e dourado)
const P = TIMBRADO
  ? { AZUL: "D4A646", AZUL_ESCURO: "E9C877", CINZA: "B5AC98", TEXTO: "EFE9DC", FUNDO_CAB: "B98F3A", TEXTO_CAB: "0B0A08",
      LINHA: "15130F", ZEBRA: "1F1B15", BORDA: "6B5527", CODIGO: "1A1814", CITACAO: "1E1A12", COR_CODIGO: "E9C877" }
  : { AZUL: "1351B4", AZUL_ESCURO: "0C326F", CINZA: "5F6B7A", TEXTO: "1F2328", FUNDO_CAB: "1351B4", TEXTO_CAB: "FFFFFF",
      LINHA: null, ZEBRA: "F2F5FA", BORDA: "C5CEDB", CODIGO: "F4F6F8", CITACAO: "EAF1FB", COR_CODIGO: "0C326F" };
const { AZUL, AZUL_ESCURO, CINZA, FUNDO_CAB, ZEBRA, BORDA } = P;
// Margens: 2 cm no padrão; no timbrado, a área de texto fica entre o cabeçalho e o selo do papel.
const MARGEM = TIMBRADO ? { top: 2780, right: 1270, bottom: 3520, left: 1270, header: 1400, footer: 400 }
  : { top: 1134, right: 1134, bottom: 1134, left: 1134 };
const LARGURA = 11906 - MARGEM.left - MARGEM.right; // largura útil em DXA
const FONTE = "Arial";

// ---------------------------------------------------------------- imagens
function tamanhoImagem(buf) {
  if (buf[0] === 0x89 && buf[1] === 0x50) return { tipo: "png", w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  if (buf[0] === 0xff && buf[1] === 0xd8) { // JPEG: procura o marcador SOF
    let i = 2;
    while (i < buf.length) {
      if (buf[i] !== 0xff) { i++; continue; }
      const m = buf[i + 1];
      if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return { tipo: "jpg", w: buf.readUInt16BE(i + 7), h: buf.readUInt16BE(i + 5) };
      i += 2 + buf.readUInt16BE(i + 2);
    }
  }
  return null;
}
function imagemInline(caminho, legenda) {
  const arq = path.isAbsolute(caminho) ? caminho : path.join(BASE_MD, caminho);
  if (!fs.existsSync(arq)) return [new Paragraph({ children: runs(`[imagem não encontrada: ${caminho}]`, { italics: true, color: CINZA }) })];
  const buf = fs.readFileSync(arq);
  const t = tamanhoImagem(buf);
  if (!t) return [new Paragraph({ children: runs(`[formato de imagem não suportado: ${caminho}]`, { italics: true, color: CINZA }) })];
  const maxW = Math.floor(LARGURA / 15) - 10; // DXA -> px (96 dpi)
  const w = Math.min(maxW, t.w), h = Math.round((t.h * w) / t.w);
  const out = [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 },
    children: [new ImageRun({ type: t.tipo, data: buf, transformation: { width: w, height: Math.min(h, 520) } })] })];
  if (legenda) out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: runs(legenda, { italics: true, color: CINZA, size: 17 }) }));
  return out;
}

// ---------------------------------------------------------------- texto inline
function runs(texto, base = {}) {
  const out = [];
  const limpo = texto.replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1"); // links -> texto
  const partes = limpo.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter((p) => p !== "");
  for (const p of partes) {
    if (p.startsWith("**") && p.endsWith("**")) out.push(new TextRun({ text: p.slice(2, -2), bold: true, font: FONTE, color: P.TEXTO, ...base }));
    else if (p.startsWith("`") && p.endsWith("`")) out.push(new TextRun({ text: p.slice(1, -1), font: "Consolas", size: (base.size || 21) - 2, color: P.COR_CODIGO }));
    else out.push(new TextRun({ text: p, font: FONTE, color: P.TEXTO, ...base }));
  }
  return out.length ? out : [new TextRun({ text: "", font: FONTE })];
}

// ---------------------------------------------------------------- tabelas
function celulasDe(linha) {
  return linha.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
}

function tabela(bloco) {
  const separador = /^\s*\|?(\s*:?-{3,}:?\s*\|)*\s*:?-{3,}:?\s*\|?\s*$/;
  const linhasT = bloco.filter((l) => !separador.test(l));
  const dados = linhasT.map(celulasDe);
  const ncol = Math.max(...dados.map((r) => r.length));
  // larguras proporcionais ao conteúdo (com mínimo), somando LARGURA
  // Larguras: mínimo = maior palavra da coluna (não quebra "MOD-001" ao meio); o espaço que sobra
  // vai para as colunas de texto longo, proporcional ao tamanho do conteúdo.
  const tam = ncol > 6 ? 15 : ncol > 4 ? 17 : 19;
  const charW = tam * 5.6; // DXA aproximados por caractere em Arial no tamanho da tabela
  const extra = 200;       // margens internas da célula
  const palavras = (s) => String(s || "").replace(/[`*]/g, "").split(/\s+/);
  const minimo = Array.from({ length: ncol }, (_, i) =>
    Math.min(18, Math.max(3, ...dados.map((r, ri) => Math.max(0, ...palavras(r[i]).map((w) => w.length * (ri === 0 ? 1.2 : 1)))))) * charW + extra);
  const preferido = Array.from({ length: ncol }, (_, i) =>
    Math.max(minimo[i], Math.min(45, Math.max(0, ...dados.map((r) => String(r[i] || "").length))) * charW + extra));
  let larguras;
  const somaMin = minimo.reduce((a, b) => a + b, 0);
  if (somaMin >= LARGURA) {
    larguras = minimo.map((m) => Math.floor((m / somaMin) * LARGURA));
  } else {
    const folga = preferido.map((p, i) => p - minimo[i]);
    const somaFolga = folga.reduce((a, b) => a + b, 0) || 1;
    const sobra = LARGURA - somaMin;
    larguras = minimo.map((m, i) => Math.floor(m + (Math.min(sobra, somaFolga) * folga[i]) / somaFolga));
    const resto = LARGURA - larguras.reduce((a, b) => a + b, 0);
    if (resto > 0) { // sobra além do preferido: distribui por igual
      larguras = larguras.map((l) => l + Math.floor(resto / ncol));
    }
  }
  larguras[ncol - 1] += LARGURA - larguras.reduce((a, b) => a + b, 0);
  const borda = { style: BorderStyle.SINGLE, size: 4, color: BORDA };
  const bordas = { top: borda, bottom: borda, left: borda, right: borda };
  const linhasDocx = dados.map((r, ri) => new TableRow({ cantSplit: true,
    tableHeader: ri === 0,
    children: Array.from({ length: ncol }, (_, ci) => new TableCell({
      width: { size: larguras[ci], type: WidthType.DXA },
      borders: bordas,
      verticalAlign: VerticalAlign.CENTER,
      margins: { top: 60, bottom: 60, left: 90, right: 90 },
      shading: ri === 0 ? { fill: FUNDO_CAB, type: ShadingType.CLEAR, color: "auto" }
        : ri % 2 === 0 ? { fill: ZEBRA, type: ShadingType.CLEAR, color: "auto" }
        : P.LINHA ? { fill: P.LINHA, type: ShadingType.CLEAR, color: "auto" } : undefined,
      children: [new Paragraph({
        spacing: { before: 0, after: 0 },
        children: runs(r[ci] || "", ri === 0 ? { bold: true, color: P.TEXTO_CAB, size: tam } : { size: tam }),
      })],
    })),
  }));
  return new Table({ width: { size: LARGURA, type: WidthType.DXA }, columnWidths: larguras, rows: linhasDocx });
}

// ---------------------------------------------------------------- corpo
function corpo() {
  const filhos = [];
  let i = 0;
  let primeiroH1 = true;
  let emCodigo = false;
  while (i < linhas.length) {
    const l = linhas[i];
    if (l.trim().startsWith("```")) { emCodigo = !emCodigo; i++; continue; }
    if (emCodigo) {
      filhos.push(new Paragraph({
        shading: { fill: P.CODIGO, type: ShadingType.CLEAR, color: "auto" }, spacing: { before: 0, after: 0 },
        children: [new TextRun({ text: l || " ", font: "Consolas", size: 17, color: P.TEXTO })],
      }));
      i++; continue;
    }
    if (/^\s*\|/.test(l)) {
      const bloco = [];
      while (i < linhas.length && /^\s*\|/.test(linhas[i])) bloco.push(linhas[i++]);
      filhos.push(tabela(bloco));
      filhos.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      continue;
    }
    let m;
    if ((m = l.match(/^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$/))) {
      filhos.push(...imagemInline(m[2], m[1]));
    } else if ((m = l.match(/^# (.*)/))) {
      if (primeiroH1 && !meta.sem_capa) { primeiroH1 = false; i++; continue; } // vai para a capa
      primeiroH1 = false;
      filhos.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(m[1]) }));
    } else if ((m = l.match(/^## (.*)/))) {
      filhos.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(m[1]) }));
    } else if ((m = l.match(/^###+ (.*)/))) {
      filhos.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(m[1]) }));
    } else if ((m = l.match(/^(\s*)[-*] (.*)/))) {
      filhos.push(new Paragraph({ numbering: { reference: "marcadores", level: m[1].length >= 2 ? 1 : 0 }, children: runs(m[2]) }));
    } else if ((m = l.match(/^>\s?(.*)/))) {
      filhos.push(new Paragraph({
        shading: { fill: P.CITACAO, type: ShadingType.CLEAR, color: "auto" },
        border: { left: { style: BorderStyle.SINGLE, size: 24, color: AZUL, space: 8 } },
        spacing: { before: 120, after: 120 }, indent: { left: 200 },
        children: runs(m[1], { italics: true, color: AZUL_ESCURO }),
      }));
    } else if (/^---+\s*$/.test(l)) {
      filhos.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BORDA, space: 1 } }, children: [] }));
    } else if (l.trim() !== "") {
      filhos.push(new Paragraph({ spacing: { after: 100 }, children: runs(l.trim()) }));
    }
    i++;
  }
  return filhos;
}

// ---------------------------------------------------------------- capa
function capa() {
  const tituloH1 = (linhas.find((l) => l.startsWith("# ")) || "# Documento").slice(2);
  const titulo = meta.titulo || tituloH1;
  const pares = [
    ["Órgão", meta.orgao], ["Contrato", meta.contrato], ["Período / referência", meta.periodo],
    ["Gerado em", meta.gerado_em], ["Classificação", meta.classificacao || "Uso interno"],
  ].filter(([, v]) => v);
  const borda = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const tab = new Table({
    width: { size: LARGURA, type: WidthType.DXA }, columnWidths: [2800, LARGURA - 2800],
    rows: pares.map(([k, v]) => new TableRow({
      children: [
        new TableCell({ width: { size: 2800, type: WidthType.DXA }, borders: { top: borda, left: borda, right: borda, bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDA } },
          children: [new Paragraph({ children: [new TextRun({ text: k, bold: true, color: CINZA, font: FONTE, size: 20 })] })] }),
        new TableCell({ width: { size: LARGURA - 2800, type: WidthType.DXA }, borders: { top: borda, left: borda, right: borda, bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDA } },
          children: [new Paragraph({ children: [new TextRun({ text: String(v), font: FONTE, size: 20, color: P.TEXTO })] })] }),
      ],
    })),
  });
  const faixa = TIMBRADO
    ? new Paragraph({ spacing: { before: 600, after: 0 }, children: [new TextRun({
        text: (TIMBRADO.empresa || "").toUpperCase(), bold: true, color: AZUL, font: FONTE, size: 18, characterSpacing: 60 })] })
    : new Paragraph({ shading: { fill: AZUL, type: ShadingType.CLEAR, color: "auto" }, spacing: { before: 0, after: 0 },
        children: [new TextRun({ text: " FÁBRICA DE SOFTWARE GOVERNAMENTAL", bold: true, color: "FFFFFF", font: FONTE, size: 20 })] });
  return [
    faixa,
    new Paragraph({ spacing: { before: TIMBRADO ? 1500 : 2400, after: 240 }, children: [new TextRun({ text: titulo, bold: true, color: TIMBRADO ? "FFFFFF" : AZUL_ESCURO, font: FONTE, size: 44 })] }),
    ...(meta.subtitulo ? [new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: meta.subtitulo, color: CINZA, font: FONTE, size: 26 })] })] : [new Paragraph({ spacing: { after: 600 }, children: [] })]),
    tab,
    new Paragraph({ spacing: { before: 1800 }, children: [new TextRun({
      text: "Documento gerado a partir de registros verificáveis (git, testes, evidências e registros humanos). Itens sem registro aparecem como \"sem registro\".",
      italics: true, color: CINZA, font: FONTE, size: 17 })] }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

// ---------------------------------------------------------------- papel timbrado
function dataExtenso(iso) {
  const meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  const m = String(iso || "").match(/^(\d{4})-(\d{2})-(\d{2})/);
  return m ? `${Number(m[3])} de ${meses[Number(m[2]) - 1]} de ${m[1]}` : String(iso || "");
}
function cabecalhoTimbrado() {
  const buf = fs.readFileSync(TIMBRADO.imagem);
  const t = tamanhoImagem(buf) || { tipo: "jpg" };
  const fundo = new ImageRun({
    type: t.tipo, data: buf, transformation: { width: 794, height: 1123 },
    floating: {
      horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: 0 },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: 0 },
      behindDocument: true, allowOverlap: true, lockAnchor: true, layoutInCell: true,
      wrap: { type: TextWrappingType.NONE },
    },
  });
  const pequeno = { color: CINZA, font: FONTE, size: 16 };
  const dataBr = String(TIMBRADO.data || "").replace(/^(\d{4})-(\d{2})-(\d{2}).*/, "$3/$2/$1");
  return new Header({ children: [
    new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 20 }, children: [fundo,
      new TextRun({ text: "Nº ", ...pequeno }), new TextRun({ text: TIMBRADO.numero || "—", ...pequeno, color: P.TEXTO, bold: true })] }),
    new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      new TextRun({ text: "Data ", ...pequeno }), new TextRun({ text: dataBr || "—", ...pequeno, color: P.TEXTO }),
      new TextRun({ text: "   ·   Página ", ...pequeno }), new TextRun({ children: [PageNumber.CURRENT], ...pequeno, color: P.TEXTO }),
      new TextRun({ text: " de ", ...pequeno }), new TextRun({ children: [PageNumber.TOTAL_PAGES], ...pequeno, color: P.TEXTO })] }),
  ] });
}
function assinatura() {
  const a = TIMBRADO && TIMBRADO.assinatura;
  if (!a || !a.nome) return [];
  return [
    new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { before: 480, after: 240 },
      children: runs(`${TIMBRADO.local ? TIMBRADO.local + ", " : ""}${dataExtenso(TIMBRADO.data)}.`) }),
    new Paragraph({ keepNext: true, spacing: { after: 900 }, children: runs("Atenciosamente,") }),
    new Paragraph({ keepNext: true, indent: { right: LARGURA - 4800 }, border: { top: { style: BorderStyle.SINGLE, size: 6, color: BORDA, space: 4 } },
      children: runs(a.nome, { bold: true }) }),
    new Paragraph({ children: runs(a.cargo || "", { color: CINZA }) }),
  ];
}

function assinaturas() {
  const lista = Array.isArray(meta.assinaturas) ? meta.assinaturas : [];
  if (!lista.length) return [];
  const sem = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const larg = Math.floor(LARGURA / lista.length);
  const local = TIMBRADO && TIMBRADO.local ? TIMBRADO.local + ", " : "";
  const data = TIMBRADO && TIMBRADO.data ? dataExtenso(TIMBRADO.data) : "";
  const celula = (a) => new TableCell({
    width: { size: larg, type: WidthType.DXA }, borders: { top: sem, bottom: sem, left: sem, right: sem },
    margins: { left: 160, right: 160 },
    children: [
      new Paragraph({ spacing: { before: 700 }, border: { top: { style: BorderStyle.SINGLE, size: 6, color: BORDA, space: 4 } },
        children: runs(a.nome || " ", { bold: true }) }),
      new Paragraph({ children: runs(a.cargo || "Nome e cargo", { color: CINZA }) }),
      ...(a.entidade ? [new Paragraph({ children: runs(a.entidade, { color: CINZA }) })] : []),
    ],
  });
  return [
    ...(data ? [new Paragraph({ alignment: AlignmentType.RIGHT, keepNext: true, spacing: { before: 360, after: 60 }, children: runs(`${local}${data}.`) })] : []),
    new Table({ width: { size: LARGURA, type: WidthType.DXA }, columnWidths: lista.map(() => larg),
      borders: { top: sem, bottom: sem, left: sem, right: sem, insideHorizontal: sem, insideVertical: sem },
      rows: [new TableRow({ cantSplit: true, children: lista.map(celula) })] }),
  ];
}

// ---------------------------------------------------------------- documento
const tituloCurto = (meta.titulo || (linhas.find((l) => l.startsWith("# ")) || "# Documento").slice(2)).slice(0, 90);
const doc = new Document({
  creator: "Fábrica de Software Governamental",
  title: tituloCurto,
  styles: {
    default: { document: { run: { font: FONTE, size: 21, color: P.TEXTO } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONTE, color: AZUL },
        paragraph: { spacing: { before: 320, after: 140 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 2 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONTE, color: AZUL_ESCURO },
        paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [{ reference: "marcadores", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 270 } } } },
    ] }],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: MARGEM }, titlePage: !meta.sem_capa && !TIMBRADO },
    headers: { default: TIMBRADO ? cabecalhoTimbrado() : new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDA, space: 2 } },
      children: [new TextRun({ text: tituloCurto, color: CINZA, font: FONTE, size: 16 })] })] }) },
    footers: { default: TIMBRADO ? new Footer({ children: [new Paragraph({ children: [] })] }) : new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: `${meta.classificacao || "Uso interno"} · Fábrica de Software Governamental · Página `, color: CINZA, font: FONTE, size: 16 }),
      new TextRun({ children: [PageNumber.CURRENT], color: CINZA, font: FONTE, size: 16 }),
      new TextRun({ text: " de ", color: CINZA, font: FONTE, size: 16 }),
      new TextRun({ children: [PageNumber.TOTAL_PAGES], color: CINZA, font: FONTE, size: 16 }),
    ] })] }) },
    children: [...(meta.sem_capa ? [] : capa()), ...corpo(), ...(meta.assinaturas ? assinaturas() : assinatura())],
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(saida, buf); console.log(saida); });
