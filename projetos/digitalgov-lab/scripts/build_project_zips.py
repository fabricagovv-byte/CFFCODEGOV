from pathlib import Path
import zipfile,hashlib,json
root=Path(__file__).resolve().parents[1]
out=root/'entregas';out.mkdir(exist_ok=True)
for n in range(1,16):
    ident=f'SYS-{n:02d}';source=root/'projetos'/ident
    target=out/f'{ident}_V3_LAB.zip';manifest={}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(source.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or f.suffix in ('.db','.db-shm','.db-wal'):continue
            rel=f.relative_to(root).as_posix();z.write(f,rel);manifest[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
        z.writestr('MANIFEST_SHA256.json',json.dumps({'project':ident,'status':'LABORATORIO','sha256':manifest},ensure_ascii=False,indent=2))
    print(target.name,len(manifest),'arquivos')
