# WNDMNGR Database Schema

## Overview

This database manages wind farm and renewable energy assets with comprehensive tracking of entities, relationships, and operational data.

**Database Type:** Microsoft SQL Server
**Schema:** dbo
**Total Tables:** 30

## Table Categories

1. **References (01_REFERENCES)** - Fixed lookup/reference tables
2. **Entities (02_ENTITIES)** - Core business entities
3. **Relationships (03_RELATIONSHIPS)** - Many-to-many relationship tables
4. **Look-ups (04_LOOK_UPS)** - Farm-specific attribute tables
5. **Foreign Keys (05_FOREIGN_KEYS)** - Additional foreign key constraints
6. **Metadata (06_METADATA)** - System metadata and versioning

---

## 1. Reference Tables (01_REFERENCES)

### company_roles
Fixed reference table for company role types.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY | Role ID |
| role_name | NVARCHAR(50) | NOT NULL, UNIQUE | Role name |

**Reference Values:**
1. Asset Manager
2. Bank Domiciliation
3. Chartered Accountant
4. Co-developer
5. Customer
6. Energy Trader
7. Grid Operator
8. Legal Auditor
9. Legal Representative
10. OM Main Service Company
11. OM Service Provider
12. Portfolio
13. Project Developer
14. Substation Service Provider
15. WTG Service Provider

---

### farm_types
Fixed reference table for farm types.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY | Type ID |
| type_title | NVARCHAR(50) | NOT NULL, UNIQUE | Type name |

**Reference Values:**
1. Wind
2. Solar
3. Hybrid

---

### person_roles
Fixed reference table for person role types.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY | Role ID |
| role_name | NVARCHAR(50) | NOT NULL, UNIQUE | Role name |

**Reference Values:**
1. Administrative Deputy
2. Administrative responsible
3. Asset Manager
4. Commercial Controller
5. Control Room Operator
6. Controller Deputy
7. Controller Responsible
8. Electrical Manager
9. Environmental Department Manager
10. Field Crew Manager
11. HSE Coordination
12. Head of Technical Management
13. Key Account Manager
14. Legal Representative
15. Overseer
16. Substitute Key Account Manager
17. Substitute Technical Manager
18. Technical Manager

---

## 2. Entity Tables (02_ENTITIES)

### companies
Core company entity table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | Company unique identifier |
| name | NVARCHAR(255) | NOT NULL | Company name |

---

### employees
Employee information linked to persons.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | Employee unique identifier |
| person_uuid | NVARCHAR(36) | NOT NULL, FK → persons(uuid) | Person reference |
| trigram | NVARCHAR(3) | UNIQUE, NOT NULL | Employee trigram/initials |
| landline | INT | | Landline phone number |
| job_title | NVARCHAR(100) | NOT NULL | Job title |

---

### farms
Core farm/project entity table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | Farm unique identifier |
| spv | NVARCHAR(100) | NOT NULL | Special Purpose Vehicle name |
| project | NVARCHAR(100) | NOT NULL | Project name |
| code | NVARCHAR(10) | NOT NULL, UNIQUE | Farm code |
| farm_type_id | INT | NOT NULL, FK → farm_types(id) | Farm type reference |

---

### ice_detection_systems
Ice detection system configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | System unique identifier |
| ids_name | NVARCHAR(100) | NOT NULL | IDS name |
| automatic_stop | BIT | NOT NULL | Automatic stop enabled |
| automatic_restart | BIT | NOT NULL | Automatic restart enabled |

---

### persons
Core person entity table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | Person unique identifier |
| first_name | NVARCHAR(100) | NOT NULL | First name |
| last_name | NVARCHAR(100) | NOT NULL | Last name |
| email | NVARCHAR(255) | | Email address |
| mobile | NVARCHAR(20) | | Mobile phone number |
| person_type | NVARCHAR(50) | | Person type/category |

---

### substations
Substation entities linked to farms.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | Substation unique identifier |
| substation_name | NVARCHAR(100) | NOT NULL | Substation name |
| farm_uuid | NVARCHAR(36) | NOT NULL, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| gps_coordinates | NVARCHAR(50) | | GPS coordinates |

---

### wind_turbine_generators
Wind turbine generator entities.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | WTG unique identifier |
| serial_number | INT | NOT NULL | Serial number |
| wtg_number | NVARCHAR(50) | NOT NULL | WTG number/name |
| farm_uuid | NVARCHAR(36) | NOT NULL, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| substation_uuid | NVARCHAR(36) | NOT NULL, FK → substations(uuid) | Substation reference |
| manufacturer | NVARCHAR(100) | | Manufacturer name |
| wtg_type | NVARCHAR(50) | | WTG type/model |
| commercial_operation_date | DATE | | Commercial operation date |

---

## 3. Relationship Tables (03_RELATIONSHIPS)

### farm_company_roles
Many-to-many relationship between farms, companies, and their roles.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PK, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| company_uuid | NVARCHAR(36) | PK, FK → companies(uuid) | Company reference |
| company_role_id | INT | PK, FK → company_roles(id) | Company role reference |

**Composite Primary Key:** (farm_uuid, company_uuid, company_role_id)

---

### farm_referents
Farm referents - can be either a person or a company with a specific role.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY, DEFAULT NEWID() | Referent unique identifier |
| farm_uuid | NVARCHAR(36) | NOT NULL, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| person_role_id | INT | FK → person_roles(id) | Person role reference |
| company_role_id | INT | FK → company_roles(id) | Company role reference |
| person_uuid | NVARCHAR(36) | FK → persons(uuid) | Person reference |
| company_uuid | NVARCHAR(36) | FK → companies(uuid) | Company reference |

**Check Constraint:** Must have either (person_uuid + person_role_id) OR (company_uuid + company_role_id), not both.

---

## 4. Look-up Tables (04_LOOK_UPS)

These tables store farm-specific attributes with 1:1 or 1:many relationships to farms.

### farm_actual_performances
Actual performance data per farm per year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PK, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| year | INT | PK | Performance year |
| amount | DECIMAL(15,2) | NOT NULL | Performance amount |

**Composite Primary Key:** (farm_uuid, year)

---

### farm_administrations
Administrative details for farms (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| account_number | NVARCHAR(50) | | Account number |
| siret_number | NVARCHAR(20) | | SIRET number |
| vat_number | NVARCHAR(20) | | VAT number |
| head_office_address | NVARCHAR(255) | | Head office address |
| legal_representative | NVARCHAR(100) | | Legal representative |
| has_remit_subscription | BIT | | REMIT subscription status |
| financial_guarantee_amount | DECIMAL(15,2) | | Financial guarantee amount |
| financial_guarantee_due_date | DATE | | Financial guarantee due date |
| land_lease_payment_date | NVARCHAR(50) | | Land lease payment date |
| windmanager_subsidiary | NVARCHAR(100) | NOT NULL | WindManager subsidiary |

---

### farm_electrical_delegations
Electrical delegation information (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| in_place | BIT | NOT NULL | Delegation in place flag |
| drei_date | DATE | NOT NULL | DREI date |
| electrical_delegate_uuid | NVARCHAR(36) | NOT NULL, FK → companies(uuid) | Electrical delegate company |

---

### farm_environmental_installations
Environmental installation details (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| aip_number | NVARCHAR(50) | | AIP number |
| duty_dreal_contact | NVARCHAR(100) | | Duty DREAL contact |
| prefecture_name | NVARCHAR(100) | | Prefecture name |
| prefecture_address | NVARCHAR(255) | | Prefecture address |

---

### farm_financial_guarantees
Financial guarantee information (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| amount | DECIMAL(15,2) | | Guarantee amount |
| due_date | DATE | | Due date |

---

### farm_ice_detection_systems
Many-to-many relationship between farms and ice detection systems.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PK, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| ice_detection_system_uuid | NVARCHAR(36) | PK, FK → ice_detection_systems(uuid) | IDS reference |

**Composite Primary Key:** (farm_uuid, ice_detection_system_uuid)

---

### farm_locations
Farm location and travel information (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| map_reference | NVARCHAR(255) | | Map reference |
| country | NVARCHAR(100) | | Country |
| region | NVARCHAR(100) | | Region |
| department | NVARCHAR(100) | | Department |
| municipality | NVARCHAR(100) | | Municipality |
| arras_round_trip_distance_km | DECIMAL(10,2) | | Distance to Arras (km) |
| vertou_round_trip_duration_h | DECIMAL(10,2) | | Duration to Vertou (hours) |
| arras_toll_eur | DECIMAL(10,2) | | Toll to Arras (EUR) |
| nantes_toll_eur | DECIMAL(10,2) | | Toll to Nantes (EUR) |

---

### farm_om_contracts
O&M contract information (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| service_contract_type | NVARCHAR(100) | | Service contract type |
| contract_end_date | DATE | | Contract end date |

---

### farm_statuses
Farm operational status (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| farm_status | NVARCHAR(50) | NOT NULL | Farm status |
| tcma_status | NVARCHAR(50) | NOT NULL | TCMA status |

---

### farm_substation_details
Substation service details (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| station_count | INT | NOT NULL | Number of stations |
| substation_service_company_uuid | NVARCHAR(36) | NOT NULL, FK → companies(uuid) | Service company |

---

### farm_target_performances
Target performance data per farm per year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PK, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| year | INT | PK | Target year |
| amount | DECIMAL(15,2) | NOT NULL | Target amount |

**Composite Primary Key:** (farm_uuid, year)

---

### farm_tariffs
Tariff and contract information (1:many relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uuid | NVARCHAR(36) | PRIMARY KEY | Tariff unique identifier |
| farm_uuid | NVARCHAR(36) | NOT NULL, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| aggregator_contract_signature_date | DATE | NOT NULL | Contract signature date |
| aggregator_contract_start_date | DATE | NOT NULL | Contract start date |
| aggregator_contract_duration | INT | NOT NULL | Contract duration |
| has_active_edf_contract | BIT | NOT NULL | Active EDF contract flag |
| tariff_ppa_type | NVARCHAR(50) | NOT NULL | PPA type |
| tariff_start_date | DATE | NOT NULL | Tariff start date |
| tariff_end_date | DATE | NOT NULL | Tariff end date |
| duration | INT | NOT NULL | Duration |
| energy_price_per_kwh | DECIMAL(10,4) | NOT NULL | Energy price per kWh |
| vppa_name | NVARCHAR(100) | | VPPA name |
| vppa_start_date | DATE | | VPPA start date |
| vppa_duration | INT | | VPPA duration |
| quantity | DECIMAL(10,2) | | Quantity |
| vppa_tariff_per_mwh | DECIMAL(10,2) | | VPPA tariff per MWh |

---

### farm_tcma_contracts
TCMA contract information (1:1 relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Farm reference |
| farm_code | NVARCHAR(10) | NOT NULL | Farm code (denormalized) |
| wf_status | NVARCHAR(50) | | Wind farm status |
| tcma_status | NVARCHAR(50) | | TCMA status |
| contract_type | NVARCHAR(50) | | Contract type |
| signature_date | DATE | | Signature date |
| effective_date | DATE | | Effective date |
| beginning_of_remuneration | DATE | | Remuneration start date |
| end_date | DATE | | End date |
| compensation_rate | DECIMAL(10,4) | | Compensation rate |

---

### farm_turbine_details
Wind turbine technical details (1:1 relationship, wind farms only).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| wind_farm_uuid | NVARCHAR(36) | PRIMARY KEY, FK → farms(uuid) | Wind farm reference |
| wind_farm_code | NVARCHAR(10) | NOT NULL | Wind farm code (denormalized) |
| turbine_count | INT | NOT NULL | Number of turbines |
| manufacturer | NVARCHAR(100) | NOT NULL | Manufacturer |
| turbine_age | INT | NOT NULL | Turbine age (years) |
| supplier | NVARCHAR(100) | NOT NULL | Supplier |
| hub_height_m | DECIMAL(10,2) | NOT NULL | Hub height (meters) |
| rotor_diameter_m | DECIMAL(10,2) | NOT NULL | Rotor diameter (meters) |
| tip_height_m | DECIMAL(10,2) | NOT NULL | Tip height (meters) |
| rated_power_installed_mw | DECIMAL(10,2) | NOT NULL | Rated power (MW) |
| total_mmw | DECIMAL(10,2) | NOT NULL | Total power (MW) |
| last_toc | DATE | | Last TOC date |
| dismantling_provision_date | DATE | | Dismantling provision date |

---

## 5. Foreign Key Constraints (05_FOREIGN_KEYS)

Additional foreign key constraints applied after table creation:

### employees
- **fk_employees_person:** person_uuid → persons(uuid)

### substations
- **fk_substations_farm:** farm_uuid → farms(uuid)

### wind_turbine_generators
- **fk_wtg_farm:** farm_uuid → farms(uuid)
- **fk_wtg_substation:** substation_uuid → substations(uuid)

---

## 6. Metadata Tables (06_METADATA)

### ingestion_versions
Tracks data ingestion versions with validation and audit trail.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | IDENTITY(1,1), PRIMARY KEY | Version ID |
| version_number | INT | NOT NULL, UNIQUE | Version number |
| ingestion_date | DATETIME | NOT NULL, DEFAULT GETDATE() | Ingestion timestamp |
| ingestion_source | VARCHAR(100) | NOT NULL | Source (github-actions, manual, etc.) |
| triggered_by | VARCHAR(255) | | GitHub username, local user, etc. |
| commit_sha | VARCHAR(40) | | Git commit SHA if applicable |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'in_progress' | Status (in_progress, completed, failed) |
| tables_affected | INT | | Number of tables loaded |
| total_rows_inserted | INT | | Total rows across all tables |
| execution_time_seconds | INT | | Duration of ingestion |
| validation_passed | BIT | | Overall validation result |
| test_silver_gold_reconciliation | BIT | | Silver to Gold row count match |
| test_uuid_integrity | BIT | | UUIDs valid and unique |
| test_foreign_keys | BIT | | Foreign key relationships valid |
| test_required_fields | BIT | | Required fields populated |
| validation_errors | NVARCHAR(MAX) | | JSON array of validation errors |
| error_message | NVARCHAR(MAX) | | Error details if failed |
| notes | NVARCHAR(500) | | Optional notes |

**Indexes:**
- IX_ingestion_versions_date ON ingestion_date DESC
- IX_ingestion_versions_status ON status
- IX_ingestion_versions_validation ON validation_passed

---

## Entity Relationship Diagram (Text)

```
farm_types (1) ----< (N) farms (1) ----< (N) substations (1) ----< (N) wind_turbine_generators
                           |
                           +----< (N) farm_company_roles >---- (N) companies
                           |                                        |
                           +----< (N) farm_referents               |
                           |          |                             |
                           |          +---- (N) person_roles        |
                           |          |                             |
                           |          +----------------------------+
                           |          |                             |
                           |          +---- (N) company_roles       |
                           |                                        |
persons (1) ----< (N) employees                                     |
     |                                                              |
     +----< (N) farm_referents                                     |
                                                                    |
ice_detection_systems (1) ----< (N) farm_ice_detection_systems >---+
                                                    |
                                                 farms

farms (1) ---- (1) farm_administrations
     (1) ---- (1) farm_electrical_delegations
     (1) ---- (1) farm_environmental_installations
     (1) ---- (1) farm_financial_guarantees
     (1) ---- (1) farm_locations
     (1) ---- (1) farm_om_contracts
     (1) ---- (1) farm_statuses
     (1) ---- (1) farm_substation_details
     (1) ---- (1) farm_tcma_contracts
     (1) ---- (1) farm_turbine_details (wind farms only)
     (1) ----< (N) farm_actual_performances (by year)
     (1) ----< (N) farm_target_performances (by year)
     (1) ----< (N) farm_tariffs
```

---

## Key Design Patterns

### UUID-based Primary Keys
Most entity tables use NVARCHAR(36) UUIDs as primary keys for global uniqueness and integration flexibility.

### Denormalized farm_code
Many tables include a `farm_code` column alongside `farm_uuid` for query optimization and reporting convenience.

### Reference Tables
Fixed reference data (company_roles, farm_types, person_roles) uses integer IDs with pre-populated values.

### 1:1 Relationships
Farm attribute tables (farm_administrations, farm_locations, etc.) use farm_uuid as their primary key, enforcing one-to-one relationships.

### 1:Many Relationships
- farms → substations → wind_turbine_generators (hierarchical)
- farms → farm_tariffs (multiple tariffs per farm)
- farms → farm_actual_performances/farm_target_performances (time series by year)

### Many:Many Relationships
- farms ↔ companies (via farm_company_roles with role)
- farms ↔ ice_detection_systems (via farm_ice_detection_systems)

### Flexible Referents
The `farm_referents` table can reference either a person OR a company with a role, enforced by check constraint.

---

## Common Query Patterns

### Get all information for a farm
```sql
SELECT f.*, ft.type_title
FROM farms f
JOIN farm_types ft ON f.farm_type_id = ft.id
WHERE f.code = 'FARM_CODE';
```

### Get farm with all companies and their roles
```sql
SELECT f.project, c.name, cr.role_name
FROM farms f
JOIN farm_company_roles fcr ON f.uuid = fcr.farm_uuid
JOIN companies c ON fcr.company_uuid = c.uuid
JOIN company_roles cr ON fcr.company_role_id = cr.id
WHERE f.code = 'FARM_CODE';
```

### Get farm hierarchy (farm → substation → turbines)
```sql
SELECT f.project, s.substation_name, wtg.wtg_number
FROM farms f
LEFT JOIN substations s ON f.uuid = s.farm_uuid
LEFT JOIN wind_turbine_generators wtg ON s.uuid = wtg.substation_uuid
WHERE f.code = 'FARM_CODE'
ORDER BY s.substation_name, wtg.wtg_number;
```

---

## Notes

- **farm_code:** Denormalized in many tables for performance
- **UUIDs:** String format NVARCHAR(36) for compatibility
- **Dates:** Use DATE type for date-only values
- **Decimals:** Used for financial and measurement precision
- **BIT:** Used for boolean flags
- **NULL handling:** Many optional fields allow NULL
- **Validation:** ingestion_versions table tracks data quality

---

**Last Updated:** 2025-12-11
**Total Tables:** 30
**Database:** WNDMNGR.DB
