export function Paginacao({ pagina, total, porPagina, aoMudar }: { pagina: number; total: number; porPagina: number; aoMudar: (p: number) => void }) {
  const paginas = Math.max(1, Math.ceil(total / porPagina));
  return (
    <nav className="paginacao" aria-label="Paginação">
      <button type="button" disabled={pagina <= 1} onClick={() => aoMudar(pagina - 1)}>Anterior</button>
      <span>Página {pagina} de {paginas} · {total} registro(s)</span>
      <button type="button" disabled={pagina >= paginas} onClick={() => aoMudar(pagina + 1)}>Próxima</button>
    </nav>
  );
}
