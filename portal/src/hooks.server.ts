
import type { Handle } from '@sveltejs/kit';
import { v4 as uuidv4 } from 'uuid';

export const handle: Handle = async ({ event, resolve }) => {
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
