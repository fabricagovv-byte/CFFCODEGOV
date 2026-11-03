//! {{NOME}} — regras de negócio (esqueleto da fábrica).

/// Corpo JSON do endpoint de saúde.
pub fn saude() -> String {
    String::from(r#"{"status":"ok","sistema":"{{NOME}}"}"#)
}

#[cfg(test)]
mod testes {
    #[test]
    fn saude_ok() {
        assert!(super::saude().contains(r#""status":"ok""#));
    }
}
