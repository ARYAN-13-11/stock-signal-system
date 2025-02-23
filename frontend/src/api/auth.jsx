const API_URL = "http://127.0.0.1:5000";

/**
 * ✅ Generic API Fetch Function
 * - Always sends credentials (cookies) with requests
 * - Handles errors and prints detailed debugging info
 */
const fetchWithAuth = async (url, options = {}) => {
    try {
        const response = await fetch(`${API_URL}${url}`, {
            ...options,
            credentials: "include", // ✅ Ensures session cookies persist
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
            },
        });

        if (!response.ok) {
            const errorMessage = await response.json();
            console.error(`❌ API Error (${response.status}):`, errorMessage);
            throw new Error(errorMessage.error || "API Error");
        }

        return response.json();
    } catch (error) {
        console.error("❌ API Fetch Failed:", error.message);
        return { error: error.message || "Unknown error" };
    }
};

/**
 * ✅ Login Function
 * - Sends username & password to the server
 * - Ensures session cookies are set
 */
export const login = async (username, password) => {
    return fetchWithAuth("/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });
};

/**
 * ✅ Check if the user is logged in
 */
export const checkLogin = async () => {
    return fetchWithAuth("/check_login");
};

/**
 * ✅ Get User ID if logged in
 */
export const getUserId = async () => {
    return fetchWithAuth("/get_user_id");
};

/**
 * ✅ Logout Function
 */
export const logout = async () => {
    return fetchWithAuth("/logout", { method: "POST" });
};

/**
 * ✅ Debugging Helper - Check Current Session Data
 */
export const debugSession = async () => {
    return fetchWithAuth("/debug_session");
};
