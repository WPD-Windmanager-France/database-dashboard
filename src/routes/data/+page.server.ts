import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { getAllFarms, getFarmFullData, getFarmTypes, getAllCompanies, getAllCompanyRoles } from '$lib/server/db/farms';
import { getAllPersons } from '$lib/server/db/referents';

export const load: PageServerLoad = async ({ url }) => {
	const farms = await getAllFarms();

	if (farms.length === 0) {
		return { farms: [], farmData: null, farmTypes: [], persons: [], companies: [], companyRoles: [], selectedUuid: '' };
	}

	// Selected farm from URL param or default to first
	const selectedUuid = url.searchParams.get('farm') ?? farms[0].uuid;

	const farmData = await getFarmFullData(selectedUuid);
	if (!farmData) {
		throw error(404, 'Farm not found');
	}

	const [farmTypes, persons, companies, companyRoles] = await Promise.all([
		getFarmTypes(),
		getAllPersons(),
		getAllCompanies(),
		getAllCompanyRoles()
	]);

	return {
		farms,
		farmData,
		farmTypes,
		persons,
		companies,
		companyRoles,
		selectedUuid
	};
};
