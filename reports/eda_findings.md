# EDA Findings

_Synthetic data — not official GridSense data._

## Overall Statistics
- Total consumption: 829,222.61 kWh
- Valid observations: 228,331
- Mean: 3.6317 | Median: 2.044 | Std: 3.6892
- Min: 0.03 | Max: 20.025 | P95: 11.861

## Finding 1 — Peak Demand Hour
- Peak aggregate demand occurs at **17:00**.
- Low demand occurs at **4:00**.
- Peak avg aggregate demand: 345.69 kWh
- Low avg aggregate demand: 230.78 kWh

## Finding 2 — Customer Segment Differences
- Highest mean consumption segment: **Industrial** (9.1323 kWh/reading)
- Segment summary:
       segment   mean  median      total    std  count
    Commercial 3.0330   2.916 173145.196 1.3488  57087
    Industrial 9.1323   8.226 521337.837 2.9204  57087
   Residential 0.8182   0.656  46692.755 0.5453  57067
Small Business 1.5422   1.301  88046.824 0.9475  57090

## Weather Correlations (system-level)
- temperature: r = 0.6807
- humidity: r = -0.2119
- rain: r = -0.0341

## Weekday vs Weekend
- Weekday mean: 3.7087 kWh | Weekend mean: 3.4369 kWh

## Tariff Period
peak_period   mean  median      total  count
   Off-Peak 3.3230   1.371 237220.770  71387
       Peak 4.6470   3.260 364730.707  78487
   Shoulder 2.8968   1.645 227271.135  78457
