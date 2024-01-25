import { jwtVerify } from "jose";

const SECRET = "test_secret_key";
export async function verifyJwtToken(token) {
    try {
      const { payload } = await jwtVerify(token, new TextEncoder().encode(SECRET));
      return payload;
    } catch (error) {
      console.error("verifyJwtToken error:", error);
      return null;
    }
  }