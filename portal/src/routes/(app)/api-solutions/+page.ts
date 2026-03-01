import { PUBLIC_ENABLE_API_SOLUTIONS } from '$env/static/public';
import { error } from '@sveltejs/kit';

export const load = () => {
    if (PUBLIC_ENABLE_API_SOLUTIONS !== 'true') {
        throw error(404, 'Not Found');
    }
    return {};
};
