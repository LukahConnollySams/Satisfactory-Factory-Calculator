from dataclasses import dataclass


@dataclass
class Building:

    name: str
    cost: dict[str, int | float]
    power: int | float
    outputs: int

    def __str__(self):

        print(self.name)

    def __hash__(self) -> int:
        
        return hash(self.name)

    def overclock(self, clock_speed: int|float):
        """
        Calculates the overclocking power consumption of the building.

        Parameters
        ----------
        clock_speed : int | float
            Overclocking percentage.

        Returns
        -------
        float
            Power consumption of builing whilst overclocked.
        """
        from math import log
        return self.power * (clock_speed /100) ** log(2.5)
