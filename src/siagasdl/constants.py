from selenium.webdriver.common.by import By


URL_BUSCA = 'https://siagasweb.sgb.gov.br/layout/pesquisa_complexa.php'

ID_BACIA = "baciahidrografica"
ID_PAGINACAO = 'pager'
SCRIPT_BUSCAR = "abrirPag('resultado_busca.php');"
SCRIPT_PAGINACAO = "javascript:paginacao({});"

BACIAS = (
    "Atlantico Sul-Leste",
    "Atlantico Sul-N/NE",
    "Atlantico Sul-Sudeste",
    "Rio Amazonas",
    "Rio Parana",
    "Rio São Francisco",
    "Rio Tocantins",
    "Rio Uruguai"
)

DISPLAY_VALUES = (
    'none',
    'inline',
    'block',
    'inline-block'
)

# used in arguments of WeElement selectors
ATTR_SELECTOR = {
    "id": By.ID,
    "name": By.NAME,
    "xpath": By.XPATH,
    "tag name": By.TAG_NAME,
    "link text": By.LINK_TEXT,
    "class name": By.CLASS_NAME,
    "css selector": By.CSS_SELECTOR,
    "partial link text": By.PARTIAL_LINK_TEXT,
}

DISPATCH_ENTER = """var ke = new KeyboardEvent('keydown', {
    bubbles: true, cancelable: true, keyCode: 13
});
arguments[0].dispatchEvent(ke);
"""
DISPATCH_ENTER_SELECTOR = (
    "var ke = new KeyboardEvent('keydown', \{"
    "   bubbles: true, cancelable: true, keyCode: 13"
    "\});"
    "{}.dispatchEvent(ke);"
)
