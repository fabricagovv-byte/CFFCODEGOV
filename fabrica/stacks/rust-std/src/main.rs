use std::io::{Read, Write};
use std::net::TcpListener;

fn main() -> std::io::Result<()> {
    let porta = std::env::var("PORT").unwrap_or_else(|_| "8000".into());
    let ouvinte = TcpListener::bind(format!("0.0.0.0:{porta}"))?;
    for conexao in ouvinte.incoming() {
        let mut c = conexao?;
        let mut buf = [0u8; 1024];
        let n = c.read(&mut buf)?;
        let pedido = String::from_utf8_lossy(&buf[..n]);
        let (status, corpo) = if pedido.starts_with("GET /api/health ") {
            ("200 OK", {{SLUG_RUST}}::saude())
        } else {
            ("404 Not Found", String::from(r#"{"erro":"não encontrado"}"#))
        };
        write!(c, "HTTP/1.1 {status}\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{corpo}", corpo.len())?;
    }
    Ok(())
}
