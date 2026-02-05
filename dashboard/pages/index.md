# Wind Manager Dashboard

```sql farms_list
SELECT
    uuid,
    code,
    project,
    spv
FROM supabase.farms
ORDER BY project
```

<Dropdown
    name=selected_farm
    data={farms_list}
    value=uuid
    label=project
    title="Sélectionner une ferme"
/>

{#if inputs.selected_farm}

```sql farm_info
SELECT
    f.code,
    f.project,
    f.spv,
    ft.type_title as farm_type
FROM supabase.farms f
LEFT JOIN supabase.farm_types ft ON f.farm_type_id = ft.id
WHERE f.uuid = '${inputs.selected_farm}'
```

```sql farm_location
SELECT
    country,
    region,
    department,
    municipality,
    map_reference
FROM supabase.farm_locations
WHERE farm_uuid = '${inputs.selected_farm}'
```

```sql farm_status
SELECT
    farm_status,
    tcma_status
FROM supabase.farm_statuses
WHERE farm_uuid = '${inputs.selected_farm}'
```

```sql farm_turbines
SELECT
    turbine_count,
    manufacturer,
    hub_height_m,
    rotor_diameter_m,
    rated_power_installed_mw,
    total_mmw
FROM supabase.farm_turbine_details
WHERE wind_farm_uuid = '${inputs.selected_farm}'
```

```sql farm_referents_list
SELECT
    COALESCE(p.first_name || ' ' || p.last_name, c.name) as referent_name,
    COALESCE(pr.role_name, cr.role_name) as role
FROM supabase.farm_referents fr
LEFT JOIN supabase.persons p ON fr.person_uuid = p.uuid
LEFT JOIN supabase.companies c ON fr.company_uuid = c.uuid
LEFT JOIN supabase.person_roles pr ON fr.person_role_id = pr.id
LEFT JOIN supabase.company_roles cr ON fr.company_role_id = cr.id
WHERE fr.farm_uuid = '${inputs.selected_farm}'
```

## {farm_info[0].project}

<BigValue
    data={farm_info}
    value=farm_type
    title="Type"
/>

<BigValue
    data={farm_info}
    value=spv
    title="SPV"
/>

### Localisation

<DataTable data={farm_location} />

### Statut

<DataTable data={farm_status} />

### Caractéristiques Turbines

{#if farm_turbines.length > 0}
<DataTable data={farm_turbines} />
{:else}
<Alert>Pas de données turbines pour cette ferme</Alert>
{/if}

### Référents

{#if farm_referents_list.length > 0}
<DataTable data={farm_referents_list} />
{:else}
<Alert>Pas de référents pour cette ferme</Alert>
{/if}

{:else}

<Alert status="info">
    Sélectionnez une ferme pour voir ses informations
</Alert>

{/if}

---

## Navigation

*Pages à venir : API Rotorsoft, Rapports Maintenance*
