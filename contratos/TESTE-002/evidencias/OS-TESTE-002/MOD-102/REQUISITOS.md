# Requisitos — MOD-102 Cadastro de protocolos

| ID | Requisito | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|
| MOD-102-1 | Incluir/detalhar | app/modulos/protocolos/router.py | test_criar_e_detalhar | IMPLEMENTADO |
| MOD-102-2 | Listar paginado e buscar | router.py | test_listar_paginado / test_busca_por_texto | IMPLEMENTADO |
| MOD-102-3 | Alterar | router.py | test_alterar | IMPLEMENTADO |
| MOD-102-4 | Excluir logicamente | router.py | test_excluir_logicamente | IMPLEMENTADO |
| MOD-102-5 | Validações (obrigatórios, tamanho, listas, CPF/CNPJ, únicos, relacionamentos) | schemas.py / router.py | test_obrigatorios, test_tamanho_*, test_enum_*, test_cpf_*, test_unico_*, test_referencia_* | IMPLEMENTADO |
| MOD-102-6 | Auditoria e LGPD | router.py | test_auditoria_registrada | IMPLEMENTADO |
| MOD-102-7 | Permissão por perfil | router.py | test_permissao_de_escrita | IMPLEMENTADO |
| MOD-102-8 | Tela com lista, busca e formulário | frontend/src/modulos/protocolos/ | ProtocoloPagina.test.tsx | IMPLEMENTADO |
