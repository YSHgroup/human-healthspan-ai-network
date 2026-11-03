import { createApiClient } from "@healthspan/api-client";

/** One typed client per portal; requests go through this portal's same-origin BFF proxy. */
export const api = createApiClient();
