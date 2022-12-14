# batttweaker.py - a fonte de dados do LeshtoBatt
import configparser
import os

# batttweaker depende de:
from driver import Battery # interface de leitura da bateria
from config.tweaker import APP, DIR # nomes dos arquivos de configuração do tweaker
from config.constants import *
from data.messages import * # mensagens de erros do tweaker


def log(str_to_print):
  print(str_to_print)

class LeshtoBatt(Battery):
    """Este é o LeshtoBatt, o leitor da bateria"""

    def __init__(self, dirpath = None):
        if dirpath is not None:
            super().__init__(dirpath, False)
        else:
            super().__init__(check_unit = False)

        self.settings = DEFAULT_SETTINGS
        # tempo da última modificação do arquivo
        self.settings_mtime = None
        # evita segundo carregamento das configurações em um app que verifica
        # ... por alterações em loop
        self.check_settings()

        self.load_settings()
        if not self._unit_checked:
            self.get_unit()
            try:
                self.save_settings()
            except:
                pass
                # Esses erros de inicialização não são relevantes

    def load_settings(self):
        """Carrega o arquivo de configurações"""
        appconf = configparser.ConfigParser()
        try:
            appconf.read(APP)
        except:
            self.error_settings()
            return
        try:
            self.got_error_settings
            del self.got_error_settings
        except:
            pass

        if len(appconf) <= 1:
            return

        # Unidade de carga
        try:
            self._unit = appconf['batt']['unit']
            self._unit_checked = True
        except:
            return # na primeira vez, tentaremos novamente...

        # Parâmetros do app
        settings = {}
        try:
            settings['level_min'] = int(appconf['batt']['level_min'])
            settings['level_max'] = int(appconf['batt']['level_max'])
            settings['level_fix'] = appconf['batt'].getboolean('level_fix')
            settings['voltage_typ'] = float(appconf['batt']['voltage_typ'])
        except:
            pass # Alguma coisa não tem

        # A ideia é que alguma coisa possa ser lida
        if not not settings:
            try:
                self.valid_settings(settings)
            except AssertionError:
                print('LeshtoBatt.load_settings(): valores inválidos ignorados')
            except KeyError:
                pass

    def valid_settings(self, settings):
        """Válida os parâmetros lidos antes de aplicar as configurações"""
        # TODO: dependendo do arquivo de configuração, alguns parâmetros não
        # ... serão lidos
        level_min = settings['level_min']
        log('LeshtoBatt.valid_settings(): level_min >= ' + str(MIN_LEVEL_MIN))
        assert level_min >= MIN_LEVEL_MIN
        log('LeshtoBatt.valid_settings(): level_min <= ' + str(MAX_LEVEL_MIN))
        assert level_min <= MAX_LEVEL_MIN

        level_max = settings['level_max']
        log('LeshtoBatt.valid_settings(): level_max >= ' + str(MIN_LEVEL_MAX))
        assert level_max >= MIN_LEVEL_MAX
        log('LeshtoBatt.valid_settings(): level_max <= ' + str(MAX_LEVEL_MAX))
        assert level_max <= MAX_LEVEL_MAX
        log('LeshtoBatt.valid_settings(): level_max > level_min')
        assert level_max > level_min

        self.settings['level_min'] = level_min
        self.settings['level_max'] = level_max

        level_fix = settings['level_fix']
        self.settings['level_fix'] = level_fix

        voltage_typ = settings['voltage_typ']
        log('LeshtoBatt.valid_settings(): voltage_typ >= '
            + str(MIN_VOLTAGE_TYP))
        assert voltage_typ >= MIN_VOLTAGE_TYP
        self.settings['voltage_typ'] = voltage_typ

    def check_settings(self):
        """Verifica mudanças no arquivo de configurações"""
        try:
            mtime = os.path.getmtime(APP)
        except FileNotFoundError:
            return False

        if self.settings_mtime is None:
            self.settings_mtime = mtime
            return True

        if self.settings_mtime != mtime:
            log('LeshtoBatt.check_settings(): changed')
            self.settings_mtime = mtime
            return True
        else:
            return False

    def save_settings(self):
        """Salva as configurações no arquivo."""
        appconf = configparser.ConfigParser()
        try:
            appconf.read(APP)
        except:
            self.error_settings()
            raise SyntaxError('O arquivo de configurações está corrompido!')

        appconf['batt'] = {
            'unit': self.get_unit(),
            'level_min': self.settings['level_min'],
            'level_max': self.settings['level_max'],
            'level_fix': self.settings['level_fix'],
        }
        if self.settings['voltage_typ'] is not None:
            appconf['batt']['voltage_typ'] = self.settings['voltage_typ']

        os.makedirs(DIR, exist_ok=True)
        with open(APP, 'w') as fconf:
            fconf.write("# MODIFICAR ISTO INCORRETAMENTE QUEBRARÁ O PROGRAMA!\n\n")
            appconf.write(fconf)

    def error_settings(self):
        """Avisa sobre erro na configuração pelo console."""
        title = ERROR_SETTINGS_TITLE % (APP)
        msg = ERROR_SETTINGS_MSG

        try:
            self.got_error_settings
            return
        except NameError:
            self.got_error_settings = True

        print(title)
        print(msg)

    def percent(self):
        p = super().percent()
        lmin = self.settings['level_min']
        lmax = self.settings['level_max']

        if self.settings['level_fix']:
            enow = self.energy_now()
            cap = self.capacity()
            if enow and cap:
                fnow = enow-lmin*cap/100
                fcap = cap*(lmax-lmin)/100
                p = fnow/fcap
            else:
                p = (p-lmin)/(lmax-lmin)
            p = int(p*100)
            if p < 0:
                p = 0
            elif p > 100:
                p = 100

        return p

    def capacity(self):
        c = super().capacity()

        if self.settings['level_fix'] and c is not None:
            d = self.settings['level_min']
            d += (100-self.settings['level_max'])
            c = c - c*(d/100)

        return c

    def energy_now(self):
        enow = super().energy_now()

        if self.settings['level_fix'] and enow is not None:
            d = self.settings['level_min']
            enow = enow - enow*(d/100)

        return enow

print('batttweaker by Leshto')
