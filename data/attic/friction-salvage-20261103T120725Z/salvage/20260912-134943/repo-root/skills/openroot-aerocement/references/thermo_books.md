# Thermo books (MODEL until H-003)

Peak noon, 1 m2 collector, AM1.5. Locked constants used in README and aerocement_ledger.py.

## Collector book (sun-on-face)

- Incident 1000 W = 3.60 MJ per peak hour
- Absorbed alpha 0.98 = 980 W (OPEN, needs ASTM E903)
- Net to air 931 W = 3.35 MJ (design constant in calc_solar)
- First Law on this face closes at or below 1000 W

## Node book (open loop)

- Coolth 35 C outdoor to 12.8 C ground class at mdot 0.0185 kg/s = 413 W = 1.49 MJ
- Service ratio 1.34 = (3.35 + 1.49) / 3.60
- Latent 0.5 kg/h = 314 W is exported vapor unless condensed. Do not add to tank pile.
- 2 C / 35 F air is TARGET not this table
- Night-sky lid scales with lid area, weak in humid Sikeston

## Forbidden labels (N14)

- Not 134 percent efficient sunlight
- Not 220 percent / 2197 W
- Not COP 21972
- Not 2500-4000 psi (unauthored band; H1 is >=15 MPa OPEN until C39)
- Not protein-foam cubic-yard ticket as the AeroCement mix

## Mix (public base)

NightHawkInLight kitchen gel. Video https://www.youtube.com/watch?v=z4_GxPHwqkA
15 g xanthan + splash alcohol + 60 ml Dawn Ultra + 1 L water, sit 5-10 min.
1 part gel : 2 parts Portland by volume.
OpenRoot deltas optional: carbon, AR-glass >=20 percent Zr, stator, 21-day wet (N13).

## Rival books (same 1 m2 hour)

- PV electric 180-220 W = 0.65-0.79 MJ (0.18-0.22)
- PV + heat pump COP 3-3.5 = 0.54-0.77 of face, heat or cold not both
- Grid fuel to shaft 0.10-0.26 of primary
- Grid fuel to resistance heat 0.30-0.38 of primary

## Separate organs

- Steam / RMH boiler is not the air loop compounding to boil
- TEG 3-5 percent of heat that crosses modules at this dT
- Stirling+alternator ~60 W_e spends hot-book slice
- HHO torch from that electric is a downgrade (~46 W heat, ~1 Pa extra stack)
- Fair-weather sky wire is nW-uW. Not a book.

## Pattern before detail

Sikeston pulse + 55 F ground + humid wet-bulb + coppice.
Then two tanks + stack + disk/RMH + lid coil.
Then gel, carbon, fiber, sensors.
Ionosphere wire and space elevator are not this node's next pour.
