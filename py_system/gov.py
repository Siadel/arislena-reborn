from dataclasses import dataclass

from py_system.tableobj import Faction, Population, Livestock, Resource, Territory, Building
from py_system._global import main_db

@dataclass
class Government:

    faction: Faction
    populations: list[Population] | bool = True
    livestocks: list[Livestock] | bool = True
    resources: list[Resource] | bool = True
    territories: list[Territory] | bool = True
    buildings: list[Building] | bool = True

    def __post_init__(self):

        p = main_db.fetch_many("population", faction_id=self.faction.id) if self.populations    else []
        l = main_db.fetch_many("livestock", faction_id=self.faction.id)  if self.livestocks     else []
        rs = main_db.fetch_many("resource", faction_id=self.faction.id)  if self.resources      else []
        t = main_db.fetch_many("territory", faction_id=self.faction.id)  if self.territories    else []
        b = [main_db.fetch("building", territory_id=territory["id"]) for territory in t if t] if self.buildings else []
        b = [building for building in b if building]
        
        self.populations = [Population.from_data(data) for data in p if p]
        self.livestocks = [Livestock.from_data(data) for data in l if l]
        self.resources = [Resource.from_data(data) for data in rs if rs]
        self.territories = [Territory.from_data(data) for data in t if t]
        self.buildings = [Building.from_data(data) for data in b if b]