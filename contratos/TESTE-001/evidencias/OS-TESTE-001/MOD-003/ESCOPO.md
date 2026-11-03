# Escopo — MOD-003 Upload de PDF

- Contrato: TESTE-001 (fictício) · OS: OS-TESTE-001

## Descrição
Envio de PDF vinculado a documento, com validação de extensão, assinatura %PDF-, tamanho máximo, nome sanitizado, hash SHA-256 e download autenticado.

## Funcionalidades
- POST /api/documentos/{id}/arquivos
- GET /api/arquivos/{id}
- Componente UploadPdf com validação no cliente

## Fora do escopo
- Antivírus
- OCR / indexação do conteúdo do PDF
