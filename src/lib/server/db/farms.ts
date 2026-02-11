import { supabase } from '$lib/server/supabase';
import type {
	FarmWithType,
	FarmStatus,
	FarmLocation,
	FarmTurbineDetails,
	FarmAdministration,
	FarmOMContract,
	FarmTCMAContract,
	FarmElectricalDelegation,
	FarmEnvironmentalInstallation,
	FarmFinancialGuarantee,
	FarmPerformance,
	FarmCompanyRoleDisplay,
	FarmFullData,
	Company,
	CompanyRole,
	FarmCompanyRole,
	WtgProduction10m
} from '$lib/types/farm';

/** List all farms with type for the sidebar selector */
export async function getAllFarms(): Promise<FarmWithType[]> {
	const { data, error } = await supabase
		.from('farms')
		.select('uuid, code, project, spv, farm_type_id, farm_types(type_title)')
		.order('project');

	if (error) throw error;

	return (data ?? []).map((f: any) => ({
		uuid: f.uuid,
		code: f.code,
		project: f.project,
		spv: f.spv,
		farm_type_id: f.farm_type_id,
		farm_type: f.farm_types?.type_title ?? 'N/A'
	}));
}

/** Get a single farm by UUID with its type */
export async function getFarmByUuid(uuid: string): Promise<FarmWithType | null> {
	const { data, error } = await supabase
		.from('farms')
		.select('uuid, code, project, spv, farm_type_id, farm_types(type_title)')
		.eq('uuid', uuid)
		.single();

	if (error) return null;

	return {
		uuid: data.uuid,
		code: data.code,
		project: data.project,
		spv: data.spv,
		farm_type_id: data.farm_type_id,
		farm_type: (data as any).farm_types?.type_title ?? 'N/A'
	};
}

export async function getFarmStatus(farmUuid: string): Promise<FarmStatus | null> {
	const { data, error } = await supabase
		.from('farm_statuses')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmLocation(farmUuid: string): Promise<FarmLocation | null> {
	const { data, error } = await supabase
		.from('farm_locations')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmTurbineDetails(farmUuid: string): Promise<FarmTurbineDetails | null> {
	const { data, error } = await supabase
		.from('farm_turbine_details')
		.select('*')
		.eq('wind_farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmAdministration(farmUuid: string): Promise<FarmAdministration | null> {
	const { data, error } = await supabase
		.from('farm_administrations')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmOMContract(farmUuid: string): Promise<FarmOMContract | null> {
	const { data, error } = await supabase
		.from('farm_om_contracts')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmTCMAContract(farmUuid: string): Promise<FarmTCMAContract | null> {
	const { data, error } = await supabase
		.from('farm_tcma_contracts')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmElectricalDelegation(farmUuid: string): Promise<FarmElectricalDelegation | null> {
	const { data, error } = await supabase
		.from('farm_electrical_delegations')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmEnvironmentalInstallation(farmUuid: string): Promise<FarmEnvironmentalInstallation | null> {
	const { data, error } = await supabase
		.from('farm_environmental_installations')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmFinancialGuarantee(farmUuid: string): Promise<FarmFinancialGuarantee | null> {
	const { data, error } = await supabase
		.from('farm_financial_guarantees')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.single();

	if (error) return null;
	return data;
}

export async function getFarmActualPerformances(farmUuid: string): Promise<FarmPerformance[]> {
	const { data, error } = await supabase
		.from('farm_actual_performances')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.order('year');

	if (error) return [];
	return data ?? [];
}

export async function getFarmTargetPerformances(farmUuid: string): Promise<FarmPerformance[]> {
	const { data, error } = await supabase
		.from('farm_target_performances')
		.select('*')
		.eq('farm_uuid', farmUuid)
		.order('year');

	if (error) return [];
	return data ?? [];
}

export async function getFarmCompanyRoles(farmUuid: string): Promise<FarmCompanyRoleDisplay[]> {
	const { data, error } = await supabase
		.from('farm_company_roles')
		.select('company_uuid, company_role_id, companies(name), company_roles(role_name)')
		.eq('farm_uuid', farmUuid);

	if (error) return [];

	return (data ?? []).map((r: any) => ({
		role_name: r.company_roles?.role_name ?? 'N/A',
		company_name: r.companies?.name ?? 'N/A',
		company_uuid: r.company_uuid,
		company_role_id: r.company_role_id
	}));
}

/** Load all data for a given farm */
export async function getFarmFullData(farmUuid: string): Promise<FarmFullData | null> {
	const farm = await getFarmByUuid(farmUuid);
	if (!farm) return null;

	const [
		status,
		location,
		turbineDetails,
		administration,
		omContract,
		tcmaContract,
		electricalDelegation,
		environmentalInstallation,
		financialGuarantee,
		actualPerformances,
		targetPerformances,
		companyRoles
	] = await Promise.all([
		getFarmStatus(farmUuid),
		getFarmLocation(farmUuid),
		getFarmTurbineDetails(farmUuid),
		getFarmAdministration(farmUuid),
		getFarmOMContract(farmUuid),
		getFarmTCMAContract(farmUuid),
		getFarmElectricalDelegation(farmUuid),
		getFarmEnvironmentalInstallation(farmUuid),
		getFarmFinancialGuarantee(farmUuid),
		getFarmActualPerformances(farmUuid),
		getFarmTargetPerformances(farmUuid),
		getFarmCompanyRoles(farmUuid)
	]);

	// Referents loaded separately (complex join)
	const { getReferentsByFarm } = await import('./referents');
	const referents = await getReferentsByFarm(farmUuid);

	return {
		farm,
		status,
		location,
		turbineDetails,
		administration,
		omContract,
		tcmaContract,
		electricalDelegation,
		environmentalInstallation,
		financialGuarantee,
		referents,
		companyRoles,
		actualPerformances,
		targetPerformances
	};
}

/** Update farm fields (SPV, project, farm_type_id) */
export async function updateFarm(uuid: string, fields: Partial<Pick<FarmWithType, 'spv' | 'project' | 'farm_type_id'>>) {
	const { error } = await supabase
		.from('farms')
		.update(fields)
		.eq('uuid', uuid);

	if (error) throw error;
}

/** Upsert farm location */
export async function upsertFarmLocation(farmUuid: string, farmCode: string, fields: Partial<FarmLocation>) {
	const { error } = await supabase
		.from('farm_locations')
		.upsert({ farm_uuid: farmUuid, farm_code: farmCode, ...fields });

	if (error) throw error;
}

/** Get all companies (for dropdown) */
export async function getAllCompanies(): Promise<Company[]> {
	const { data, error } = await supabase
		.from('companies')
		.select('uuid, name')
		.order('name');

	if (error) return [];
	return data ?? [];
}

/** Get all company role types (for dropdown) */
export async function getAllCompanyRoles(): Promise<CompanyRole[]> {
	const { data, error } = await supabase
		.from('company_roles')
		.select('id, role_name')
		.order('role_name');

	if (error) return [];
	return data ?? [];
}

/** Get company role ID by name */
export async function getCompanyRoleByName(roleName: string): Promise<number | null> {
	const { data, error } = await supabase
		.from('company_roles')
		.select('id')
		.eq('role_name', roleName)
		.single();

	if (error) return null;
	return data.id;
}

/** Upsert a farm company role assignment */
export async function upsertFarmCompanyRole(
	farmUuid: string,
	farmCode: string,
	companyRoleId: number,
	companyUuid: string,
	oldCompanyUuid?: string
) {
	// If changing company for an existing role, delete old first
	if (oldCompanyUuid && oldCompanyUuid !== companyUuid) {
		await supabase
			.from('farm_company_roles')
			.delete()
			.eq('farm_uuid', farmUuid)
			.eq('company_role_id', companyRoleId)
			.eq('company_uuid', oldCompanyUuid);
	}

	const { error } = await supabase
		.from('farm_company_roles')
		.upsert({
			farm_uuid: farmUuid,
			farm_code: farmCode,
			company_role_id: companyRoleId,
			company_uuid: companyUuid
		});

	if (error) throw error;
}

/** Delete a farm company role assignment */
export async function deleteFarmCompanyRole(
	farmUuid: string,
	companyRoleId: number,
	companyUuid: string
) {
	const { error } = await supabase
		.from('farm_company_roles')
		.delete()
		.eq('farm_uuid', farmUuid)
		.eq('company_role_id', companyRoleId)
		.eq('company_uuid', companyUuid);

	if (error) throw error;
}

/** Create a new company */
export async function createCompany(company: { uuid: string; name: string }) {
	const { error } = await supabase
		.from('companies')
		.insert(company);

	if (error) throw error;
}

/** Upsert farm administration */
export async function upsertFarmAdministration(farmUuid: string, farmCode: string, fields: Partial<FarmAdministration>) {
	const { error } = await supabase
		.from('farm_administrations')
		.upsert({ farm_uuid: farmUuid, farm_code: farmCode, ...fields });
	if (error) throw error;
}

/** Upsert farm O&M contract */
export async function upsertFarmOMContract(farmUuid: string, farmCode: string, fields: Partial<FarmOMContract>) {
	const { error } = await supabase
		.from('farm_om_contracts')
		.upsert({ farm_uuid: farmUuid, farm_code: farmCode, ...fields });
	if (error) throw error;
}

/** Upsert farm TCMA contract */
export async function upsertFarmTCMAContract(farmUuid: string, farmCode: string, fields: Partial<FarmTCMAContract>) {
	const { error } = await supabase
		.from('farm_tcma_contracts')
		.upsert({ farm_uuid: farmUuid, farm_code: farmCode, ...fields });
	if (error) throw error;
}

/** Upsert farm financial guarantee */
export async function upsertFarmFinancialGuarantee(farmUuid: string, farmCode: string, fields: Partial<FarmFinancialGuarantee>) {
	const { error } = await supabase
		.from('farm_financial_guarantees')
		.upsert({ farm_uuid: farmUuid, farm_code: farmCode, ...fields });
	if (error) throw error;
}

/** Upsert farm electrical delegation */
export async function upsertFarmElectricalDelegation(farmUuid: string, farmCode: string, fields: Partial<FarmElectricalDelegation>) {
	const { error } = await supabase
		.from('farm_electrical_delegations')
		.upsert({ farm_uuid: farmUuid, farm_code: farmCode, ...fields });
	if (error) throw error;
}

/** Upsert farm environmental installation */
export async function upsertFarmEnvironmentalInstallation(farmUuid: string, farmCode: string, fields: Partial<FarmEnvironmentalInstallation>) {
	const { error } = await supabase
		.from('farm_environmental_installations')
		.upsert({ farm_uuid: farmUuid, farm_code: farmCode, ...fields });
	if (error) throw error;
}

/** Get recent production data for a farm (via wind_turbine_generators → wtg_production_10m) */
export async function getFarmProduction(farmUuid: string, hours: number = 24): Promise<WtgProduction10m[]> {
	// Step 1: Get turbine rotorsoft_ids for this farm
	const { data: turbines, error: turbineError } = await supabase
		.from('wind_turbine_generators')
		.select('rotorsoft_id, wtg_number')
		.eq('farm_uuid', farmUuid)
		.not('rotorsoft_id', 'is', null);

	if (turbineError || !turbines || turbines.length === 0) return [];

	const puIds = turbines.map((t: any) => t.rotorsoft_id).filter(Boolean);
	if (puIds.length === 0) return [];

	// Step 2: Get production data for last N hours
	const since = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();

	const { data, error } = await supabase
		.from('wtg_production_10m')
		.select('pu_id, timestamp, active_power_avg_kw, wind_speed_avg_ms, op_state')
		.in('pu_id', puIds)
		.gte('timestamp', since)
		.order('timestamp', { ascending: true });

	if (error) return [];
	return data ?? [];
}

/** Get all farm types */
export async function getFarmTypes() {
	const { data, error } = await supabase
		.from('farm_types')
		.select('*')
		.order('id');

	if (error) return [];
	return data ?? [];
}
