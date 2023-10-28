"""
    Package "siagasdl"

    This module provides package's api
"""
import logging

from .collector import Crawler

from .constants import URL_BUSCA
from .constants import BACIAS
from .constants import ID_BACIA
from .constants import SCRIPT_BUSCAR
from .constants import SCRIPT_PAGINACAO

from .utils import make_selector

logger = logging.getLogger('client')


selector_iframe = make_selector(
    '//iframe[@src="tabular.php"]', 'xpath'
)
selector_anchors = make_selector(
    '//a[contains(@href, "detalhe.php")]', 'xpath'
)
selector_display_paginacao = make_selector(
    '//input[@class="pagedisplay"]', 'xpath'
)


class SiagasCollector(Crawler):
    """
    Classe SiagasCollector para coletar dados do site Siagas.

    Esta classe estende a classe Crawler e fornece métodos para pesquisa e
    coleta de dados relacionados a diferentes bacias hidrográficas.

    Parâmetros:
    ----------
    quit_on_failure : bool, opcional
        Se True, o rastreador encerra em caso de falha, por padrão, False.
    timeout : int, opcional
        O tempo máximo de espera para o carregamento de elementos na página, por padrão 20.
    debug : bool, opcional
        Se True, habilita o modo de depuração, por padrão, False.
    print_exc_limit : None ou int, opcional
        O limite para o número de exceções a serem impressas, por padrão None.
    **kwargs : dict, opcional
        Argumentos adicionais a serem passados para a classe Crawler base.

    Atributos:
    ----------
    links : list
        Uma lista para armazenar os links coletados.
    busca : str
        Uma string para armazenar a consulta de pesquisa atual.

    Métodos:
    -------
    busca_por_bacia(bacia, inicio=1, fim=None)
        Pesquisa e coleta de dados para uma bacia hidrográfica especificada.

    save_links(mode='w')
        Salva os links coletados em um arquivo.

    load_links(filename)
        Carrega os links de um arquivo para continuar uma pesquisa.

    continua_busca_por_bacia(filename, bacia, fim=None)
        Continua uma pesquisa a partir de uma lista de links carregada.

    """
    def __init__(self,
                 quit_on_failure: bool = False,
                 timeout: int = 20,
                 debug=False,
                 print_exc_limit=None,
                 **kwargs):
        """
        Inicializa a instância do SiagasCollector.

        Parâmetros:
        ----------
        quit_on_failure : bool, opcional
            Se True, o rastreador encerra em caso de falha, por padrão, False.
        timeout : int, opcional
            O tempo máximo de espera para o carregamento de elementos na página, por padrão 20.
        debug : bool, opcional
            Se True, habilita o modo de depuração, por padrão, False.
        print_exc_limit : None ou int, opcional
            O limite para o número de exceções a serem impressas, por padrão None.
        **kwargs : dict, opcional
            Argumentos adicionais a serem passados para a classe Crawler base.

        Retorna:
        --------
        None
        """
        super().__init__(
            quit_on_failure, timeout, debug, print_exc_limit, **kwargs
        )
        self.goto(URL_BUSCA)
        self.switch_to_frame(**selector_iframe)
        self.links = []
        self.busca = ''

    def busca_por_bacia(self, bacia: str, inicio=1, fim: int = None):
        """
        Pesquisa e coleta de dados para uma bacia hidrográfica especificada.

        Parâmetros:
        ----------
        bacia : str
            O nome da bacia hidrográfica a ser pesquisada.
        inicio : int, opcional
            A página inicial para a coleta de dados, por padrão 1.
        fim : int, opcional
            A página final para a coleta de dados, por padrão None.
            Se nenhum for fornecido, todas as páginas serão coletadas.

        Retorna:
        --------
        None

        Levanta:
        ------
        ValueError
            Se a bacia hidrográfica especificada não estiver na lista predefinida.
        """
        try:
            bacia_index = BACIAS.index(bacia)
        except ValueError as err:
            message = "O valor de bacia deve ser um destes:\n"
            message += "\n".join(BACIAS)
            self.close()
            raise ValueError(message) from err

        # apenas para identificação da busca
        self.busca = bacia.replace(' ', '_').replace('-', '_')
        self.busca = self.busca.replace('/', '_')
        
        n_arrow_down = bacia_index + 1  # ordem o item do menu Bacias Hidro
        menu_bacia = self.find(ID_BACIA)  # menu dropdown de Bacias Hidro
        # seleciona a bacia
        self.arrow_down_element(menu_bacia, n_times=n_arrow_down)
        logger.info("Iniciando a coleta.")
        # executa a busca
        self.run(SCRIPT_BUSCAR)
        # extrai links
        anchors = self.find_elements(**selector_anchors)
        
        if inicio == 1:
            self.links.extend(
                [anchor.get_attribute('href') for anchor in anchors]
            )
            self.save_links()
        
            logger.info("Primeira página extraída.")
        # informações da paginação
        pagedisplay = self.find(**selector_display_paginacao)
        ini, fin = pagedisplay.get_attribute('value').split(' de ')
        pagina_atual, pagina_final = int(ini), int(fin)
        
        # valores iniciais de busca (caso continue de um estado anterior)
        if inicio > 1:
            pagina_atual = inicio - 1
        if fim and fim < pagina_final:
            pagina_final = fim

        logger.info(
            "Número de resultados: %s; começando por: %s", fin, pagina_atual
        )
        logger.info("Coletando dados até a página %s", pagina_final)
        
        while pagina_atual < pagina_final:
            
            paginacao = 30*pagina_atual
            # executa paginação
            self.run(SCRIPT_PAGINACAO.format(paginacao))
            # extrai os links
            anchors = self.find_elements(**selector_anchors)
            self.links.extend(
                [anchor.get_attribute('href') for anchor in anchors]
            )
            # informações da paginação
            pagedisplay = self.find(**selector_display_paginacao)
            ini, fin = pagedisplay.get_attribute('value').split(' de ')
            pagina_atual = int(ini)

            # a cada 10 páginas, salva os links
            if pagina_atual % 10 == 0:
                self.save_links()

    def save_links(self, mode='w'):
        """
        Salva os links coletados em um arquivo.

        Parâmetros:
        ----------
        mode : str, opcional
            O modo de abertura do arquivo, por padrão 'w'.

        Retorna:
        --------
        None
        """
        with open(f"{self.busca}.txt", mode, encoding='utf-8') as file_:
            file_.write('\n'.join(self.links))


    def load_links(self, filename: str):
        """
        Carrega os links de um arquivo para continuar uma pesquisa.

        Parâmetros:
        ----------
        filename : str
            O nome do arquivo para carregar os links.

        Retorna:
        --------
        None
        """
        with open(filename, 'r', encoding='utf-8') as file_:
            links_str = file_.read()
            self.links = links_str.split('\n')

    def continua_busca_por_bacia(self,
                                 filename: str,
                                 bacia: str,
                                 fim: int = None):
        """
        Continua uma pesquisa a partir de uma lista de links carregada.

        Parâmetros:
        ----------
        filename : str
            O nome do arquivo contendo os links a serem continuados.
        bacia : str
            O nome da bacia hidrográfica a ser pesquisada.
        fim : int, opcional
            A página final para a coleta de dados, por padrão None.

        Retorna:
        --------
        None
        """
        self.load_links(filename)
        inicio = len(self.links)//30 + 1
        self.busca_por_bacia(bacia, inicio=inicio, fim=fim)

