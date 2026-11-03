export function Alerta({ tipo = "erro", children }: { tipo?: "erro" | "sucesso" | "info"; children: React.ReactNode }) {
  if (!children) return null;
  return (
    <div className={`alerta alerta-${tipo}`} role={tipo === "erro" ? "alert" : "status"} aria-live="polite">
      {children}
    </div>
  );
}
