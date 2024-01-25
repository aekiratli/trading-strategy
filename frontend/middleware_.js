// import { NextResponse } from "next/server";
// import { verifyJwtToken } from "./utils/auth";

// const AUTH_PAGES = ["/login"];

// const isAuthPages = (url) => AUTH_PAGES.some((page) => page.startsWith(url));

// export async function middleware(request) {

//   const { url, nextUrl, cookies } = request;
//   const { value: token } = cookies.get("token") ?? { value: null };
//   const hasVerifiedToken = token && (await verifyJwtToken(token));
//   const isAuthPageRequested = isAuthPages(nextUrl.pathname);

//   if (nextUrl.pathname !== '/login') {
//     console.log("isAuthPageRequested", isAuthPageRequested);
//     console.log("hasVerifiedToken", hasVerifiedToken);

//     if (!hasVerifiedToken) {
//       console.log("redirect to login from /");
//       return NextResponse.redirect(new URL('/login', url))
//     }
//     console.log("redirect to / from /");
//     return NextResponse.next();
//   }

//   if (!hasVerifiedToken) {
//     return NextResponse.redirect(new URL('/login', url))
//   }

//   return NextResponse.next();

// }
// export const config = {
//   matcher: [
//     /*
//      * Match all request paths except for the ones starting with:
//      * - api (API routes)
//      * - _next/static (static files)
//      * - _next/image (image optimization files)
//      * - favicon.ico (favicon file)
//      */
//     '/((?!api|_next/static|_next/image|favicon.ico).*)',
//   ],
// }