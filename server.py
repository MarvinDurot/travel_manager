#
# Serveur de l'application
#

from mako.lookup import TemplateLookup
from facades import CityFacade, TravelFacade
import cherrypy
import os

# Emplacement local et emplacements des templates
_current_dir = os.path.abspath(os.path.dirname(__file__))
_template_dir = os.path.join(_current_dir, 'templates')
_module_dir = os.path.join(_template_dir, 'mako_modules')

mylookup = TemplateLookup(
    directories=[_template_dir],
    module_directory=_module_dir,
    input_encoding='utf-8',
    output_encoding='utf-8',
    encoding_errors='replace'
)

# Templates de l'application
_home = mylookup.get_template('home.mako.html')
_travel = mylookup.get_template('travel.mako.html')
_travels = mylookup.get_template('travels.mako.html')
_admin = mylookup.get_template('admin.mako.html')
_admin_travels = mylookup.get_template('admin_travels.mako.html')
# _admin_cities = mylookup.get_template('admin_cities.mako.html')


class Controller:
    """
    Contrôleur par défaut (héritage)
    """

    def __init__(self):
        self.message = None
        self.title = ''

    def setMessage(self, message):
        self.message = message

    def setTitle(self, title):
        self.title = title

    def render(self, view, **kwargs):
        return view.render_unicode(title=self.title, message=self.message, **kwargs)

    @cherrypy.expose
    def default(self):
        raise cherrypy.NotFound


class FrontendController(Controller):
    """
    Contrôleur partie frontend
    """

    def __init__(self):
        self.backend = BackendController()
        super(self.__class__, self).__init__()

    @cherrypy.expose
    def index(self):
        # self.setTitle('Accueil')
        return self.render(_home)

    @cherrypy.expose
    def travel(self, travel_id=None):
        try:
            travel = TravelFacade.find(travel_id)
        except:
            raise cherrypy.NotFound

        self.setTitle('Fiche voyage')
        return self.render(_travel, travel=travel)

    @cherrypy.expose
    def travels(self, sorting=None):
        # Tri par capital
        if sorting == 'capitals':
            travels = TravelFacade.all_capitals()
            self.setTitle('Liste des voyages concernant une capitale')
        # Tri par budget
        elif sorting == 'budget':
            travels = TravelFacade.all_by_budget()
            self.setTitle('Liste des voyages triés par budget')
        # Tri par durée de transport
        elif sorting == 'transport_duration':
            travels = TravelFacade.all_by_transport_duration()
            self.setTitle('Liste des voyages triés par durée de transport')
        # Tri par défaut
        else:
            travels = TravelFacade.all()
            self.setTitle('Liste des voyages')

        if len(travels) == 0:
            raise cherrypy.NotFound
        else:
            return self.render(_travels, travels=travels)


class BackendController(Controller):
    """
    Contrôleur de la partie backend
    """

    @cherrypy.expose
    def index(self):
        self.setTitle('Menu administration')
        return self.render(_admin)

    @cherrypy.expose
    def travels(self):
        # TODO : traiter l'ajout et la suppression de voyages
        self.setTitle('Administration des voyages')
        return self.render(_admin_travels)

    @cherrypy.expose
    def cities(self, city_id=None, name=None, is_capital=None, country=None, capital_id=None, delete=None, save=None):
        # Récupération de la ville si son id est précisé
        if city_id is None:
            travel = None
        else:
            travel = TravelFacade.find(city_id)

        # On a cliqué sur le bouton de suppression
        if delete is not None:
            self.delete_city(city_id)
        # On a cliqué sur le bouton de sauvegarde
        elif save is not None:
            if city_id == 0:
                self.create_city(name, is_capital, country, capital_id)
            else:
                self.update_city(city_id, name, is_capital, country, capital_id)

        self.setTitle('Gérer les villes')
        travels = TravelFacade.all()

        return self.render(_admin_travels, travels=travels, travel=travel)

    def update_city(self, id, name, is_capital, country, capital_id):
        """
        Met à jour une ville à partir d'informations récupérées dans un formulaire
        :param id:
        :param name:
        :param is_capital:
        :param country:
        :param capital_id:
        :return:
        """
        pass

    def create_city(self, name, is_capital, country, capital_id):
        """
        Crée une nouvelle ville à partir d'informations récupérées dans un formulaire
        :param name:
        :param is_capital:
        :param country:
        :param capital_id:
        :return:
        """
        pass

    def delete_city(self, city_id):
        """
        Supprime une ville
        :param city_id:
        :return:
        """
        try:
            TravelFacade.delete(city_id)
            self.setMessage('Suppression réussie !')
        except:
            self.setMessage('Erreur lors de la suppression !')


def validate_password(real, username, password):
    """
    Fonction de vérification du login / mot de passe
    :param real:
    :param username:
    :param password:
    :return: boolean
    """
    if username == 'admin' and password == 'admin123':
        return True
    else:
        return False


if __name__ == '__main__':
    # Configuration générale de CherryPy
    global_conf = {
        'global': {
            'autoreload.on': False,
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 8080,
            'server.protocol_version': 'HTTP/1.1',
            'server.thread_pool': 5,
            'tools.encode.encoding': 'utf-8',
            'log.error_file': os.path.join(_current_dir, 'error.log'),
            'log.screen': True
        }
    }

    # Mise à jour de la configuration de CherryPy
    cherrypy.config.update(global_conf)

    # Configuration de l'application
    app_conf = {
        'backend': {
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': '127.0.0.1',
            'tools.auth_basic.checkpassword': validate_password
        },
        '/assets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(_current_dir, 'assets')
        },
        '/assets/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(_current_dir, 'assets/css'),
            'tools.staticdir.content_types': {'css': 'text/css'}
        },
        '/assets/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(_current_dir, 'assets/js'),
            'tools.staticdir.content_types': {'js': 'application/javascript'}
        }
    }

    # Lancement du serveur
    cherrypy.quickstart(FrontendController(), '/', config=app_conf)
