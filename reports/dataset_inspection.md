# Dataset Inspection Report
_Synthetic practice data — not official GridSense data._

## meter_readings
- Shape: 229,658 rows × 3 columns
- Columns: ['timestamp', 'customer', 'consumption']
- Exact duplicate rows: 100
- Missing `consumption`: 918 (0.40%)
- dup_customer_timestamp: 180
- negative_consumption: 229
- null_consumption: 918
- invalid_timestamps: 0
- unique_customers: 80
- date_range: ['2025-01-01 00:00:00', '2025-04-30 23:00:00']

## customers
- Shape: 80 rows × 5 columns
- Columns: ['customer', 'segment', 'area', 'connection_type', 'tariff_category']
- Exact duplicate rows: 0
- unique_customers: 80
- segments_raw: ['INDUSTRIAL ', 'RESIDENTIAL', 'small business ', ' residential ', ' INDUSTRIAL', 'COMMERCIAL', ' Small Business', 'SMALL BUSINESS', 'Small Business', 'Residential', 'Commercial', 'commercial', 'Industrial', ' COMMERCIAL ', 'industrial', 'residential']
- areas: ['East', 'South', 'North', 'West', 'Central']
- connection_types: ['Three Phase', 'Single Phase', 'High Voltage']
- tariff_categories: ['TOU-C', 'TOU-A', 'TOU-B']

## weather
- Shape: 2,868 rows × 4 columns
- Columns: ['timestamp', 'temperature', 'humidity', 'rain']
- Exact duplicate rows: 0
- Missing `temperature`: 17 (0.59%)
- Missing `humidity`: 17 (0.59%)
- Missing `rain`: 17 (0.59%)
- invalid_timestamps: 0
- date_range: ['2025-01-01 00:00:00', '2025-04-30 23:00:00']

## calendar
- Shape: 120 rows × 4 columns
- Columns: ['date', 'weekday', 'holiday', 'season']
- Exact duplicate rows: 0
- unique_dates: 120
- holiday_count: 5

## tariff
- Shape: 72 rows × 4 columns
- Columns: ['tariff_category', 'hour', 'peak_period', 'tariff_rate']
- Exact duplicate rows: 0
- tariff_categories: ['TOU-A', 'TOU-B', 'TOU-C']
- peak_periods: ['Off-Peak', 'Shoulder', 'Peak']
