import { jwtVerify } from "jose";

const SECRET = process.env.NEXT_PUBLIC_JWT_SECRET;

export async function verifyJwtToken(token) {
    try {
      await jwtVerify(token, new TextEncoder().encode(SECRET));
      return true;
    } catch (error) {
      return false;
    }
  }