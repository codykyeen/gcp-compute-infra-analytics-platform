## 🔄 dbt Transformation Layer
## convert raw GCP resource data into structured, analytics-ready datasets.

### Core Responsibilities

- Normalize and clean raw data from BigQuery staging tables (`latest_*`)
- Track infrastructure state changes over time
- Enrich resources with pricing data
- Compute monthly cost for instances, disks, and snapshots
- Produce BI-ready datasets for analytics and visualization

---

### Modeling Approach

#### Incremental Models
- Used to efficiently track infrastructure state over time
- New rows are inserted only when changes are detected (via `change_hash`)
- Allows historical state tracking without full refreshes

#### Snapshots
- Used for slowly changing dimensions (SCD Type 2)
- Track lifecycle changes such as:
  - instance status changes
  - disk attachment/detachment
  - label updates
- Maintain `dbt_valid_from` and `dbt_valid_to` timestamps

---

### Cost Modeling

The system calculates infrastructure cost using seed-based pricing tables:

- **Instance Cost**
  - `hourly_price × 730` (standard GCP monthly estimate)

- **Disk Cost**
  - `SUM(size_gb × price_per_gib_month)`

- **Snapshot Cost**
  - `SUM(storage_bytes / 1073741824 × price_per_gib_month)`

All cost calculations are performed at the correct grain (resource-level) before aggregation to avoid duplication errors.

---

### Final Marts

The primary outputs are BI-ready tables:

`instance_cost_summary`

This table provides:

- One row per instance (latest state)
- Resource counts and sizes
- Monthly cost breakdown
- Flags for:
  - missing disks
  - missing snapshots
  - label inconsistencies

There is also:
`orphaned_disks.sql`

This table tracks and reports any disks not attached to a instance.

`infrastructure_summary` 

This table provides a quick snapshot of the current infrastructure state

---

### Data Quality

Data quality is enforced through dbt tests:

- ✅ `not_null` and `unique` constraints on key identifiers
- ✅ custom SQL tests for cost validation (e.g., no negative values)

Run all transformations and tests with:

```bash
dbt build
```

---

### Documentation

dbt docs generate
dbt docs serve --port 8081
Go to: http://localhost:8081