# Vídeo-conceito: plataforma da fábrica (tema preto e dourado)

Animação de 88 segundos que mostra como seria a plataforma, passando por todos os fluxos:
painel, editais, fluxo E.P.D.A., produção, código e testes, medição, equipe e horas, relatórios e continuidade.
É um **conceito**: a plataforma mostrada não existe como produto. Os números são os do contrato de demonstração TESTE-002 e do edital PE-223.

- Vídeo pronto: `distribuicao/video/plataforma_fabrica.mp4` (1920×1080, 24 quadros por segundo).
- Fonte: `plataforma.html` (abra no navegador para ver a animação em tempo real).

## Gerar de novo

```bash
cd fabrica/docs/video_plataforma
node captura.cjs plataforma.html /tmp/quadros 24          # captura quadro a quadro (precisa do Playwright)
ffmpeg -framerate 24 -i /tmp/quadros/f%05d.jpg -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
       -movflags +faststart ../../../distribuicao/video/plataforma_fabrica.mp4
```

Para mudar textos, números ou tempos, edite `plataforma.html`: cada cena tem `data-start` e `data-end` (segundos)
e cada elemento entra no tempo `data-in`, contado a partir do início da cena.
