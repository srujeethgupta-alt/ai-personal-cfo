/**
 * Convert form state (string values from inputs) into API-ready JSON.
 * - Removes user_id (backend uses authenticated user)
 * - Coerces number/int fields
 * - Turns empty date strings into null
 */
export function prepareFormPayload(data, { numbers = [], integers = [], dates = [] } = {}) {
    const payload = { ...data };
    delete payload.user_id;

    for (const key of numbers) {
        if (key in payload) {
            const raw = payload[key];
            if (raw === "" || raw === null || raw === undefined) {
                delete payload[key];
            } else {
                payload[key] = Number(raw);
            }
        }
    }

    for (const key of integers) {
        if (key in payload) {
            const raw = payload[key];
            if (raw === "" || raw === null || raw === undefined) {
                delete payload[key];
            } else {
                payload[key] = parseInt(raw, 10);
            }
        }
    }

    for (const key of dates) {
        if (key in payload && (payload[key] === "" || payload[key] === undefined)) {
            payload[key] = null;
        }
    }

    return payload;
}

export function getApiErrorMessage(error, fallback = "Failed to save") {
    const detail = error?.response?.data?.detail;
    if (Array.isArray(detail)) {
        return detail.map((d) => d.msg).join(". ");
    }
    return error?.response?.data?.error || fallback;
}
