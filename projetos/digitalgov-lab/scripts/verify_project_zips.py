"""Verifica integridade dos 15 pacotes individuais (manifestos SHA-256)."""
from pathlib import Path
import json,zipfile,hashlib,sys
root=Path(__file__).resolve().parents[1]
ok=True
for n in range(1,16):
 name=f'SYS-{n:02d}';zpath=root/'entregas'/f'{name}_V3_LAB.zip'
 if not zpath.exists():print('FALTA',zpath);ok=False;continue
 with zipfile.ZipFile(zpath) as z:
  if z.testzip():print('ZIP CORROMPIDO',name);ok=False;continue
  manifest=json.loads(z.read('MANIFEST_SHA256.json'))
  for path,sha in manifest['sha256'].items():
   if hashlib.sha256(z.read(path)).hexdigest()!=sha:
    print('HASH INVÁLIDO',name,path);ok=False
  print(name,'OK',len(manifest['sha256']),'arquivos')
sys.exit(0 if ok else 1)
