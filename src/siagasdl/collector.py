"""
    Package "supciaec"

    This module provides package's base logic, factories and abstractions
"""

import logging
import traceback
from typing import Callable

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import WebDriverException

from urllib3.exceptions import MaxRetryError
from requests.adapters import ReadTimeout
from requests.adapters import ConnectionError
from selenium.webdriver.remote.errorhandler import NoSuchWindowException
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from selenium.webdriver.remote.errorhandler import StaleElementReferenceException
from selenium.webdriver.remote.errorhandler import ElementNotInteractableException
from selenium.webdriver.remote.errorhandler import ElementClickInterceptedException

from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from lxml import etree

from .utils import Key
from .utils import document_query_selector
from .utils import document_query_selector_all
from .utils import is_display
from .constants import ATTR_SELECTOR
from .constants import DISPATCH_ENTER
from .constants import DISPATCH_ENTER_SELECTOR

# typing
WebElement = webdriver.remote.webelement.WebElement
WebElements = list[WebElement]

# exceptions for quit_on_failure
EXCEPTIONS = (
    ReadTimeout,
    ConnectionError,
    NoSuchWindowException,
    NoSuchElementException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementNotInteractableException,
    ElementClickInterceptedException
)

logger = logging.getLogger("standard")
logging.getLogger('WDM').setLevel(logging.WARNING)

class Crawler:
    def __init__(self,
                 quit_on_failure: bool = False,
                 timeout: int = 20,
                 debug=False,
                 print_exc_limit=None,
                 **kwargs):
        self.quit_on_failure = quit_on_failure
        self.timeout = timeout
        self.debug = debug
        self.soup = None
        self.dom = None
        self.print_exec_limt = print_exc_limit
        self.driver = None
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())
        )

    def quitonfailure(method: Callable) -> Callable:  # pylint: disable=E0213
        """ "safe quit webdriver to avoid memory leakages"""

        def inner(self, *args, **kwargs) -> Callable:
            try:
                # pylint: disable=not-callable
                return method(self, *args, **kwargs)
            except EXCEPTIONS as err:
                if self.debug:
                    logger.error(err)
                    logger.error(traceback.format_exc())
                if self.quit_on_failure:
                    logger.warning("Closing window and quitting driver.")
                    self.close(quit_driver=True)
                    logger.warning("Driver quit.")
                    raise err  # 2

        return inner

    def is_running(self,):
        try:
            self.driver.service.assert_process_still_running()
            return True
        except WebDriverException:
            return False

    @quitonfailure
    def page_source(self):
        return self.driver.page_source

    @quitonfailure
    def reposition(
        self,
        posix: int = None,
        posiy: int = None,
    ):
        """
        Reposition window
        """
        self.driver.set_window_position(x=posix, y=posiy)

    @quitonfailure
    def resize(
        self,
        width: int = None,
        height: int = None,
    ):
        """
        Resize window
        """
        self.driver.set_window_size(width=width, height=height)

    @quitonfailure
    def resize_half_x(self, ):
        window_size = self.driver.get_window_size()
        width = int(window_size['width']/2)
        height = int(window_size['height'])
        self.resize(width=width, height=height)

    @quitonfailure
    def resize_half_y(self, ):
        window_size = self.driver.get_window_size()
        width = int(window_size['width'])
        height = int(window_size['height']/2)
        self.resize(width=width, height=height)

    @quitonfailure
    def resize_half_xy(self, ):
        window_size = self.driver.get_window_size()
        width = int(window_size['width']/2)
        height = int(window_size['height']/2)
        self.resize(width=width, height=height)

    @quitonfailure
    def goto(self, url: str):
        """open window at url"""
        self.driver.get(url)

    @quitonfailure
    def current_url(self):
        return self.driver.current_url

    @quitonfailure
    def find(
        self,
        value: str,
        by: str = "id",
        expected_condition=EC.presence_of_element_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> WebElement:
        if timeout is None:
            timeout = self.timeout
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        result = wait.until(expected_condition((ATTR_SELECTOR[by], value)))
        return result

    @quitonfailure
    def find_elements(
        self,
        value: str,
        by: str = "id",
        expected_condition=EC.presence_of_all_elements_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> list[WebElement]:
        return self.find(value, by, expected_condition, timeout, poll_frequency, ignored_exceptions)

    @quitonfailure
    def xpath(
        self,
        value: str,
        expected_condition=EC.presence_of_all_elements_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> list[WebElement]:
        return self.find_elements(
            value, "xpath", expected_condition, timeout, poll_frequency, ignored_exceptions
        )

    @quitonfailure
    def send_to(
        self,
        element: WebElement,
        key: str | Key,
        expected_condition=EC.element_to_be_clickable,
        enter=False,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        send_key similar to Window.send

        Send 'key' to WebElement 'element'

        Parameters
        ----------
        element : WebElement
            Valid WebElement from selenium.
        key : Valid Selenium key or text.

        Returns
        -------
        WebElement
            Element which key was sent to.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element)).send_keys(key)
        if enter:
            element.send_keys(Key.enter)

    @quitonfailure
    def send(
        self,
        element: WebElement,
        value: str,
        key: str | Key,
        by="id",
        expected_condition_element=EC.presence_of_element_located,
        expected_condition_send=EC.element_to_be_clickable,
        enter=False,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        element = self.find(
            value=value,
            by=by,
            expected_condition=expected_condition_element,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self.send_to(
            element,
            key,
            expected_condition=expected_condition_send,
            enter=enter,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @quitonfailure
    def descendant(
        self,
        element: WebElement,
        value: str,
        by="id",
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        descendant = wait.until(
            lambda elem: element.find_element(ATTR_SELECTOR[by], value)
        )
        return descendant

    @quitonfailure
    def descendant_by_class_name(
        self,
        element: WebElement,
        value: str,
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        descendant = wait.until(
            lambda elem: element.find_element(
                ATTR_SELECTOR['class name'], value)
        )
        return descendant

    @quitonfailure
    def descendants(
        self,
        element: WebElement,
        value: str,
        by="id",
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        offspring = wait.until(
            lambda elem: element.find_elements(ATTR_SELECTOR[by], value)
        )
        return offspring

    @quitonfailure
    def descendants_by_class_name(
        self,
        element: WebElement,
        value: str,
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        offspring = wait.until(
            lambda elem: element.find_elements(
                ATTR_SELECTOR['class name'], value)
        )
        return offspring

    @quitonfailure
    def click_element(
        self,
        element: WebElement,
        expected_condition=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element)).click()

    @quitonfailure
    def click(
        self,
        value: str,
        by="id",
        expected_condition_element=EC.presence_of_element_located,
        expected_condition_click=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        element = self.find(
            value=value,
            by=by,
            expected_condition=expected_condition_element,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self.click_element(
            element,
            expected_condition=expected_condition_click,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @quitonfailure
    def arrow_down_element(
        self,
        element: WebElement,
        n_times: int = 1,
        enter=False,
        expected_condition=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        for _ in range(n_times):
            wait.until(expected_condition(element)).send_keys(Key.down)
        if enter:
            wait.until(expected_condition(element)).send_keys(Key.enter)

    @quitonfailure
    def soup_of(
        self,
        element: WebElement,
        parser="html.parser",
        features="lxml",
        outer=True,
        **kwargs
    ):
        type_attribute = "innerHTML"
        if outer:
            type_attribute = "outerHTML"

        return BeautifulSoup(
            element.get_attribute(type_attribute),
            parser=parser,
            features=features,
            **kwargs
        )

    @quitonfailure
    def run(self, script, *args):
        return self.driver.execute_script(script, *args)

    @quitonfailure
    def query_selector(self, selector: str):
        script = document_query_selector(selector)
        return self.run(script)

    @quitonfailure
    def query_selector_all(self, selector: str):
        script = document_query_selector_all(selector)
        return self.run(script)

    @quitonfailure
    def dispatch_enter(self, element: WebElement):
        return self.run(DISPATCH_ENTER, element)

    @quitonfailure
    def dispatch_enter_selector(self, selector: str):
        return self.run(DISPATCH_ENTER_SELECTOR.format(selector))

    def is_display(self, element: WebElement, value: str):
        script = is_display(value)
        return self.run(script, element)

    @quitonfailure
    def make_soup(self, parser="html.parser", **kwargs):
        return BeautifulSoup(self.page_source(), parser=parser, **kwargs)

    @quitonfailure
    def make_dom(self, soup_parser="html.parser", **kwargs):
        self.soup = self.make_soup(parser=soup_parser)
        self.dom = etree.HTML(str(self.soup), **kwargs)
        return self.dom

    def wait(
            self,
            timeout=None,
            poll_frequency=0.5,
            ignored_exceptions=(NoSuchElementException, )
    ):
        if timeout is None:
            timeout = self.timeout
        return WebDriverWait(
            self.driver, timeout, poll_frequency, ignored_exceptions
        )

    @quitonfailure
    def tab_handle(
        self,
    ):
        return self.driver.current_window_handle

    @quitonfailure
    def tabs(
        self,
    ):
        return self.driver.window_handles

    @quitonfailure
    def switch_to_tab(self, index: int):
        tabs = self.tabs()
        if len(tabs) <= index:
            if self.debug:
                logger.warning(
                    "Trying to switch to tab nº %d, but there are only %d tabs",
                    index,
                    len(tabs),
                )
        else:
            self.driver.switch_to.window(tabs[index])

    @quitonfailure
    def close_tab(
        self,
    ):
        try:
            self.driver.close()
        except NoSuchWindowException:
            tab_index = 0
            current_tab = self.window_handle()
            for index, tab in enumerate(self.tabs()):
                if tab == current_tab:
                    tab_index = index
            client_logger.warning(
                "Tab %d no longer exists. Switching to tab 0", tab_index
            )
            self.switch_to_tab(0)

    @quitonfailure
    def switch_to_frame(self, value: str, by='id'):
        self.wait().until(
            EC.frame_to_be_available_and_switch_to_it(
                (by, value)
            )
        )

    def close(self, quit_driver=True):
        try:
            self.driver.close()
        except NoSuchWindowException:
            self.switch_to_tab(0)
            self.driver.close()
        if quit_driver:
            self.driver.quit()


class DisplayIs:
    """An expectation for checking that an element has a particular css class.

    element - used to check it's 'display' value
    returns the WebElement once it has the particular css class
    """

    def __init__(self, element, display="none"):
        self.element = element
        self.display = display

    def __call__(self, driver: webdriver):
        script = is_display(self.display)
        if driver.execute_script(script, self.element):
            return True
        else:
            return False


class CrawlerError(Exception):
    """Custom error class for scraper-related errors."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'ScraperError: {self.message}'
