// Core entities
export interface Farm {
	uuid: string;
	spv: string;
	project: string;
	code: string;
	farm_type_id: number;
}

export interface FarmWithType extends Farm {
	farm_type: string; // from join farm_types.type_title
}

export interface FarmType {
	id: number;
	type_title: string;
}

// Look-ups (1:1 with farm)
export interface FarmStatus {
	farm_uuid: string;
	farm_code: string;
	farm_status: string;
	tcma_status: string;
}

export interface FarmLocation {
	farm_uuid: string;
	farm_code: string;
	map_reference: string | null;
	country: string | null;
	region: string | null;
	department: string | null;
	municipality: string | null;
	arras_round_trip_distance_km: number | null;
	vertou_round_trip_duration_h: number | null;
	arras_toll_eur: number | null;
	nantes_toll_eur: number | null;
}

export interface FarmTurbineDetails {
	wind_farm_uuid: string;
	wind_farm_code: string;
	turbine_count: number;
	manufacturer: string;
	turbine_age: number;
	supplier: string;
	hub_height_m: number;
	rotor_diameter_m: number;
	tip_height_m: number;
	rated_power_installed_mw: number;
	total_mmw: number;
	last_toc: string | null;
	dismantling_provision_date: string | null;
}

export interface FarmAdministration {
	farm_uuid: string;
	farm_code: string;
	account_number: string | null;
	siret_number: string | null;
	vat_number: string | null;
	head_office_address: string | null;
	legal_representative: string | null;
	has_remit_subscription: boolean | null;
	financial_guarantee_amount: number | null;
	financial_guarantee_due_date: string | null;
	land_lease_payment_date: string | null;
	windmanager_subsidiary: string;
}

export interface FarmOMContract {
	farm_uuid: string;
	farm_code: string;
	service_contract_type: string | null;
	contract_end_date: string | null;
}

export interface FarmTCMAContract {
	farm_uuid: string;
	farm_code: string;
	wf_status: string | null;
	tcma_status: string | null;
	contract_type: string | null;
	signature_date: string | null;
	effective_date: string | null;
	beginning_of_remuneration: string | null;
	end_date: string | null;
	compensation_rate: number | null;
}

export interface FarmElectricalDelegation {
	farm_uuid: string;
	farm_code: string;
	in_place: boolean;
	drei_date: string;
	electrical_delegate_uuid: string;
}

export interface FarmEnvironmentalInstallation {
	farm_uuid: string;
	farm_code: string;
	aip_number: string | null;
	duty_dreal_contact: string | null;
	prefecture_name: string | null;
	prefecture_address: string | null;
}

export interface FarmFinancialGuarantee {
	farm_uuid: string;
	farm_code: string;
	amount: number | null;
	due_date: string | null;
}

// Production data (10-min resolution from Rotorsoft)
export interface WtgProduction10m {
	pu_id: string;
	timestamp: string;
	active_power_avg_kw: number | null;
	wind_speed_avg_ms: number | null;
	op_state: string | null;
}

// Performance (1:N by year)
export interface FarmPerformance {
	farm_uuid: string;
	farm_code: string;
	year: number;
	amount: number;
}

// Referents
export interface Person {
	uuid: string;
	first_name: string;
	last_name: string;
	email: string | null;
	mobile: string | null;
	person_type: string | null;
}

export interface PersonRole {
	id: number;
	role_name: string;
}

export interface CompanyRole {
	id: number;
	role_name: string;
}

export interface Company {
	uuid: string;
	name: string;
}

export interface FarmReferent {
	uuid: string;
	farm_uuid: string;
	farm_code: string;
	person_role_id: number | null;
	company_role_id: number | null;
	person_uuid: string | null;
	company_uuid: string | null;
}

export interface FarmReferentDisplay {
	referent_name: string;
	role: string;
}

// Company roles for Services tab
export interface FarmCompanyRole {
	farm_uuid: string;
	farm_code: string;
	company_uuid: string;
	company_role_id: number;
}

export interface FarmCompanyRoleDisplay {
	role_name: string;
	company_name: string;
	company_uuid: string;
	company_role_id: number;
}

// Composite: all data for a selected farm
export interface FarmFullData {
	farm: FarmWithType;
	status: FarmStatus | null;
	location: FarmLocation | null;
	turbineDetails: FarmTurbineDetails | null;
	administration: FarmAdministration | null;
	omContract: FarmOMContract | null;
	tcmaContract: FarmTCMAContract | null;
	electricalDelegation: FarmElectricalDelegation | null;
	environmentalInstallation: FarmEnvironmentalInstallation | null;
	financialGuarantee: FarmFinancialGuarantee | null;
	referents: FarmReferentDisplay[];
	companyRoles: FarmCompanyRoleDisplay[];
	actualPerformances: FarmPerformance[];
	targetPerformances: FarmPerformance[];
}
