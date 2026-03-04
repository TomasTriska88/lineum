import { i18n } from '$lib/i18n';
import { sequence } from '@sveltejs/kit/hooks';
import type { Handle } from '@sveltejs/kit';
import { v4 as uuidv4 } from 'uuid';

const sessionHandle: Handle = async ({ event, resolve }) => {
    let sessionId = event.cookies.get('session_id');

    if (!sessionId) {
        sessionId = uuidv4();
        event.cookies.set('session_id', sessionId, {
            path: '/',
            httpOnly: true,
            sameSite: 'strict',
            maxAge: 60 * 60 * 24 * 30 // 30 days
        });
    }

    event.locals.sessionId = sessionId;

    const response = await resolve(event);
    return response;
};

// Important for Paraglide i18n routing: i18n.handle() must run first!
export const handle = sequence(i18n.handle(), sessionHandle);