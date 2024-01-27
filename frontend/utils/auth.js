import { jwtVerify } from "jose";

const SECRET = "test_secret_key";
export async function verifyJwtToken(token) {
    try {
      await jwtVerify(token, new TextEncoder().encode(SECRET));
      return true;
    } catch (error) {
      return false;
    }
  }