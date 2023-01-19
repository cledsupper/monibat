# batteryinterface.py - Leshto Battery Interface Prototype
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

# Usado pelos módulos:
# -> driver, config.tweaker

from typing import Optional


class BatteryInterface:
    """Interface Battery para padronizar o acesso aos dados da bateria."""

    def __init__(self, check_unit: bool = True):
        pass

    def refresh(self):
        """Atualiza o conjunto de dados retornados pelo driver."""
        raise NotImplementedError('Battery.refresh not implemented yet')

    @property
    def unit(self) -> str:
        self.refresh()
        return self._unit

    @property
    def percent(self) -> int:
        """Nível de carga da bateria em percentual"""
        self.refresh()
        return self._percent

    @property
    def charging(self) -> bool:
        """Retorna se a bateria está carregando."""
        self.refresh()
        return self._charging

    @property
    def capacity(self) -> Optional[float]:
        """Retorna a capacidade estimada da bateria em Watts ou Amperes"""
        self.refresh()
        return self._capacity

    @property
    def capacity_design(self) -> Optional[float]:
        """Retorna a capacidade típica da bateria em Watts ou Amperes"""
        self.refresh()
        return self._capacity_design

    @property
    def energy_now(self) -> Optional[float]:
        """Retorna o nível de carga da bateria em Watts ou Amperes"""
        self.refresh()
        return self._energy_now

    @property
    def current_now(self) -> Optional[float]:
        """Retorna a velocidade da (des)carga em Watts ou Amperes"""
        self.refresh()
        return self._current_now

    @property
    def temp(self) -> Optional[float]:
        """Temperatura da bateria (ºC)"""
        self.refresh()
        return self._temp

    @property
    def voltage(self) -> Optional[float]:
        """Tensão da bateria (V)"""
        self.refresh()
        return self._voltage

    @property
    def health(self) -> Optional[str]:
        """Saúde da bateria"""
        self.refresh()
        return self._health

    @property
    def technology(self) -> Optional[str]:
        """Tecnologia da bateria (Li-ion, Li-poly, etc.)"""
        self.refresh()
        return self._technology

    @property
    def status(self) -> str:
        """Status da bateria: Charging, Discharging, Unknown, ..."""
        self.refresh()
        return self._status
