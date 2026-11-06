import json, sys, urllib.request, urllib.error, datetime, hashlib, pathlib
saida = pathlib.Path(sys.argv[1])
res = []
def chamar(url, corpo=None):
    req = urllib.request.Request(url, method="POST" if corpo is not None else "GET",
                                 data=None if corpo is None else json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")
for n in range(1, 16):
    base = f"http://127.0.0.1:{8000 + n}"
    st_m, meta = chamar(base + "/api/service/metadata")
    amostra = meta.get("sample") or (meta.get("metadata") or {}).get("sample")
    st_ok, ok = chamar(base + "/api/service/run", amostra)
    st_neg, neg = chamar(base + "/api/service/run", {"invalid": True})
    st_h, hist = chamar(base + "/api/service/history")
    r = {"projeto": f"SYS-{n:02d}", "servico": meta.get("name"), "descricao": meta.get("description"),
         "executado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
         "positivo": {"http": st_ok, "entrada": amostra, "resposta": ok},
         "negativo": {"http": st_neg, "entrada": {"invalid": True}, "resposta": neg},
         "historico_registros": len(hist.get("items", [])) if isinstance(hist, dict) else None}
    corpo = json.dumps(r, ensure_ascii=False, indent=2)
    (saida / f"SYS-{n:02d}.json").write_text(corpo, encoding="utf-8")
    res.append({"projeto": r["projeto"], "servico": r["servico"], "positivo_http": st_ok, "negativo_http": st_neg,
                "sha256": hashlib.sha256(corpo.encode()).hexdigest()[:16]})
(saida / "RESUMO.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
for x in res:
    print(f"{x['projeto']} {x['positivo_http']} / {x['negativo_http']}  {x['servico']}")
