import { decodeJwt } from "jose";

export async function verifyJwtToken(token) {
    try {
      const decoded = decodeJwt(token);
      const currentTimestamp = Math.floor(Date.now() / 1000);
      if (decoded.exp < currentTimestamp) {
        // Token has expired
        return false;
      }
      return true;
    } catch (error) {
      return false;
    }
}