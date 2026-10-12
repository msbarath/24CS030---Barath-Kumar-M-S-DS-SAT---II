# Preprocessing Audit

_Synthetic data — not official GridSense data._

## meter_readings
- rows_input: 229658
- exact_dupes_removed: 100
- conflicting_key_dupes_removed: 80
- invalid_timestamps_removed: 0
- negative_consumption_found: 229
- null_consumption_rows: 918
- iqr_flagged_high: 2
- rows_output: 229249

## customers
- rows_input: 80
- segments_after_norm: ['Industrial', 'Residential', 'Small Business', 'Commercial']
- duplicate_customer_ids: 0
- rows_output: 80

## weather
- rows_input: 2868
- invalid_timestamps_removed: 0
- missing_temperature: 17
- missing_humidity: 17
- missing_rain: 17
- rows_output: 2868

## calendar
- rows_output: 120

## tariff
- rows_output: 72

## integration
- meter_rows_before_join: 229249
- meter_unmatched_customers: 0
- rows_after_customer_join: 229249
- meter_unmatched_weather: 957
- rows_after_weather_join: 229249
- meter_unmatched_calendar: 0
- rows_after_calendar_join: 229249
- meter_unmatched_tariff: 0
- rows_after_tariff_join: 229249
