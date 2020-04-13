import logging

logger = logging.getLogger(__name__)


class Document:
    def __init__(self, form_id: str, contract_number: object, form: object):
        self.__form_id = form_id
        self.__contract_number = contract_number
        self.__form = form
        logger.debug('Created document: Form ID - {}, Contract Number - {}'.format(self.get_form_id(), self.get_contract_number()))

    def get_form_id(self):
        return self.__form_id

    def set_form_id(self, form_id):
        self.__form_id = form_id

    def get_contract_number(self):
        return self.__contract_number

    def set_contract_number(self, contract_number):
        self.__contract_number = contract_number

    def get_form(self):
        return self.__form

    def set_form(self, form):
        self.__form = form
