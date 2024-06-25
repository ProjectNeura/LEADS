from typing import Any as _Any

from matplotlib.pyplot import figure as _figure, scatter as _scatter, show as _show, title as _title, \
    colorbar as _colorbar, bar as _bar, xticks as _xticks, legend as _legend, xlabel as _xlabel, ylabel as _ylabel

from leads.data import dlat2meters, dlon2meters, format_duration
from leads.data_persistence.analyzer.processor import Processor
from .._computational import sqrt as _sqrt


class StaticProcessor(Processor):
    def draw_lap(self, lap_index: int = -1) -> None:
        if lap_index < 0:
            for i in range(len(self._laps)):
                self.draw_lap(i)
        if lap_index >= len(self._laps):
            raise IndexError("Lap index out of range")

        def unit(row: dict[str, _Any], index: int) -> None:
            if index < (lap := self._laps[lap_index])[0] or index > lap[1]:
                return
            t = int(row["t"])
            if self._lap_start_time is None:
                self._lap_start_time = t
            self._lap_end_time = t
            lat = row["latitude"]
            lon = row["longitude"]
            self._lap_d.append(row["speed"])
            self._lap_x.append(x := dlon2meters(lon - self._min_lon, lat))
            self._lap_y.append(y := dlat2meters(lat - self._min_lat))
            if self._max_lap_x is None or x > self._max_lap_x:
                self._max_lap_x = x
            if self._max_lap_y is None or y > self._max_lap_y:
                self._max_lap_y = y

        self.foreach(unit, True, True)
        far = max(self._max_lap_x, self._max_lap_y)
        self._lap_x.append(far)
        self._lap_y.append(far)
        self._lap_d.append(self._max_speed)
        _figure(figsize=(6, 5))
        _title(f"Lap {lap_index + 1} ({self._laps[lap_index][3]:.2f} KM @ {format_duration(
            self._laps[lap_index][2] * .001)})")
        _scatter(self._lap_x, self._lap_y, c=self._lap_d, cmap="hot_r")
        _xlabel("X (M)")
        _ylabel("Y (M)")
        cb = _colorbar()
        cb.set_label("Speed (KM / H)")
        cb.ax.hlines(self._laps[lap_index][4], 0, 1)
        _show()

    def draw_comparison_of_laps(self, width: float = .3) -> None:
        durations = []
        x0 = []
        distances = []
        x1 = []
        avg_speeds = []
        x2 = []
        x_ticks = []
        i = 1
        for lap in self._laps:
            durations.append(lap[2] / self._max_lap_duration)
            x0.append(i)
            distances.append(lap[3] / self._max_lap_distance)
            x1.append(i + width)
            avg_speeds.append(lap[4] / self._max_lap_avg_speed)
            x2.append(i + 2 * width)
            x_ticks.append(f"L{i}")
            i += 1
        _figure(figsize=(5 * _sqrt(len(self._laps)), 5))
        _bar(x0, durations, width, label="Duration")
        _bar(x1, distances, width, label="Distance")
        _bar(x2, avg_speeds, width, label="Average Speed")
        _xticks(x1, x_ticks)
        _legend()
        _xlabel("Lap")
        _ylabel("Proportion (% / max)")
        _show()
