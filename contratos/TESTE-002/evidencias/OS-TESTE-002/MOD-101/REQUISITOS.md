# Requisitos — MOD-101 Cadastro de interessados

| ID | Requisito | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|
| MOD-101-1 | Incluir/detalhar | app/modulos/interessados/router.py | test_criar_e_detalhar | IMPLEMENTADO |
| MOD-101-2 | Listar paginado e buscar | router.py | test_listar_paginado / test_busca_por_texto | IMPLEMENTADO |
| MOD-101-3 | Alterar | router.py | test_alterar | IMPLEMENTADO |
| MOD-101-4 | Excluir logicamente | router.py | test_excluir_logicamente | IMPLEMENTADO |
| MOD-101-5 | Validações (obrigatórios, tamanho, listas, CPF/CNPJ, únicos, relacionamentos) | schemas.py / router.py | test_obrigatorios, test_tamanho_*, test_enum_*, test_cpf_*, test_unico_*, test_referencia_* | IMPLEMENTADO |
| MOD-101-6 | Auditoria e LGPD | router.py | test_auditoria_registrada | IMPLEMENTADO |
| MOD-101-7 | Permissão por perfil | router.py | test_permissao_de_escrita | IMPLEMENTADO |
| MOD-101-8 | Tela com lista, busca e formulário | frontend/src/modulos/interessados/ | InteressadoPagina.test.tsx | IMPLEMENTADO |
