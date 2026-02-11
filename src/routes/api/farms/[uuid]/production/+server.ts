import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getFarmByUuid, getFarmProduction } from '$lib/server/db/farms';

export const GET: RequestHandler = async ({ params, url }) => {
	const farm = await getFarmByUuid(params.uuid);
	if (!farm) throw error(404, 'Farm not found');

	const hours = Number(url.searchParams.get('hours') ?? '24');
	const data = await getFarmProduction(farm.uuid, hours);

	return json(data);
};
