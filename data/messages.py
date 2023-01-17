# messages.py - Messages which can be shown on MoniBat's GUI
#
#  Copyright (c) 2022, 2023 Cledson Ferreira
#
#  Author: Cledson Ferreira <cledsonitgames@gmail.com>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA

# Utilizado pelos módulos:
# tweaker, notify

TWEAKER_CFG_READ_SUCCESS = 'configuração atualizada'
TWEAKER_CFG_READ_FAILED = 'erro de config., cód.: %d'

TWEAKER_CFG_SAVE_FAILED = 'falha ao salvar configuração!'

EVENTS_ADB_CHECK_WARNING = 'Verificão da depuração ADB pode levar %d segs'

EVENTS_RECALIBRATE_START_MESSAGE = 'carregue a bateria completamente para continuar'
EVENTS_RECALIBRATE_START_TITLE = 'calibração da bateria iniciada ℹ'

EVENTS_RECALIBRATE_PARTIAL_MESSAGE = 'descarregue a bateria até %d %%'
EVENTS_RECALIBRATE_PARTIAL_TITLE = 'calibração final da bateria ℹ'

EVENTS_RECALIBRATE_FINISH_MESSAGE = 'resultado: %0.2f Ah'
EVENTS_RECALIBRATE_FINISH_TITLE = 'bateria calibrada! ✅'

EVENTS_ALARM_PERCENT_TITLE = 'aviso de carga'
EVENTS_ALARM_PERCENT_HIGH_MESSAGE = 'Desconecte o carregador para preservar a saúde da bateria'

EVENTS_ALARM_PERCENT_LOW_MESSAGE = 'Conecte o carregador para preservar a saúde da bateria'
EVENTS_ALARM_PERCENT_LOW_TITLE = 'bateria fraca 📉'

EVENTS_ALARM_TEMPERATURE_MAX_TOAST = '📵 A BATERIA VAI EXPLODIR! 📵'
EVENTS_ALARM_TEMPERATURE_MAX_MESSAGE = '📵 DESLIGUE O CELULAR AGORA! 📵'
EVENTS_ALARM_TEMPERATURE_MAX_TITLE = 'A BATERIA VAI EXPLODIR 🧨 🔥'

EVENTS_ALARM_TEMPERATURE_TITLE = 'aviso de temperatura'
EVENTS_ALARM_TEMPERATURE_HIGH_WHEN_DISCHARGING = 'Habilite a economia da energia para esfriar a bateria'
EVENTS_ALARM_TEMPERATURE_HIGH_WHEN_CHARGING = 'Desconecte o carregador para esfriar a bateria'

EVENTS_ALARM_TEMPERATURE_MIN_MESSAGE = 'O desempenho da bateria deve piorar bastante! 📉'

EVENTS_ALARM_STATUS_CONNECTED = 'O conector foi conectado 🔌🔋'
EVENTS_ALARM_STATUS_DISCONNECTED = 'O conector foi desconectado 🔋'

NOTIFY_BATTERY_STATUS_TITLE = 'estado da bateria'
NOTIFY_BATTERY_STATUS_BUTTON_RECALIBRATE = 'recalibrar'
NOTIFY_BATTERY_STATUS_BUTTON_RESTART = 'reiniciar'
NOTIFY_BATTERY_STATUS_BUTTON_EXIT = 'encerrar'
NOTIFY_BATTERY_STATUS_REMAINING_DAYS = '%d dia(s) e %d h restantes'
NOTIFY_BATTERY_STATUS_REMAINING_HOURS = '%d h e %d mins restantes'
NOTIFY_BATTERY_STATUS_REMAINING_MINS = '%d min e %d s restantes'

NOTIFY_MESSAGE_TITLE = 'mensagem do serviço'
