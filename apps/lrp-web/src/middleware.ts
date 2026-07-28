import { NextResponse, type NextRequest } from 'next/server';
import { CRM_ACCESS_COOKIE, CRM_SESSION_COOKIE } from '@/lib/crm/config';
import { LENDER_ACCESS_COOKIE, LENDER_SESSION_COOKIE } from '@/lib/lender/config';
import { PLATFORM_ACCESS_COOKIE } from '@/lib/platform/config';
import { REALTOR_ACCESS_COOKIE, REALTOR_SESSION_COOKIE } from '@/lib/realtor/config';

function hasAnyCookie(request: NextRequest, names: string[]) {
  return names.some((name) => Boolean(request.cookies.get(name)?.value));
}

const REALTOR_PUBLIC_PREFIXES = [
  '/realtor/login',
  '/realtor/activate',
  '/realtor/forgot-password',
  '/realtor/reset-password',
];

function isRealtorPublic(pathname: string) {
  return REALTOR_PUBLIC_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isPortalAuthPage =
    pathname.startsWith('/portal/login') ||
    pathname.startsWith('/portal/signup') ||
    pathname.startsWith('/portal/forgot-password') ||
    pathname.startsWith('/portal/auth');

  const isPortalApp = pathname.startsWith('/portal') && !isPortalAuthPage;
  const hasPortalSession = Boolean(request.cookies.get(PLATFORM_ACCESS_COOKIE)?.value);

  if (isPortalApp && !hasPortalSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/portal/login';
    url.searchParams.set('redirect', pathname);
    return NextResponse.redirect(url);
  }

  if (isPortalAuthPage && hasPortalSession && pathname.startsWith('/portal/login')) {
    const url = request.nextUrl.clone();
    url.pathname = '/portal/dashboard';
    return NextResponse.redirect(url);
  }

  const isLenderLogin = pathname.startsWith('/lender/login');
  const isLenderApp = pathname.startsWith('/lender') && !isLenderLogin;
  const hasLenderSession = hasAnyCookie(request, [LENDER_ACCESS_COOKIE, LENDER_SESSION_COOKIE]);

  if (isLenderApp && !hasLenderSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/lender/login';
    url.searchParams.set('redirect', pathname);
    return NextResponse.redirect(url);
  }

  if (isLenderLogin && hasLenderSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/lender/dashboard';
    return NextResponse.redirect(url);
  }

  const isCrmLogin = pathname.startsWith('/crm/login');
  const isCrmApp = pathname.startsWith('/crm') && !isCrmLogin;
  const hasCrmSession = hasAnyCookie(request, [CRM_ACCESS_COOKIE, CRM_SESSION_COOKIE]);

  if (isCrmApp && !hasCrmSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/crm/login';
    url.searchParams.set('redirect', pathname);
    return NextResponse.redirect(url);
  }

  if (isCrmLogin && hasCrmSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/crm/dashboard';
    return NextResponse.redirect(url);
  }

  const isRealtorPublicPath = isRealtorPublic(pathname);
  const isRealtorApp = pathname.startsWith('/realtor') && !isRealtorPublicPath;
  const hasRealtorSession = hasAnyCookie(request, [REALTOR_ACCESS_COOKIE, REALTOR_SESSION_COOKIE]);

  if (isRealtorApp && !hasRealtorSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/realtor/login';
    url.searchParams.set('redirect', pathname);
    return NextResponse.redirect(url);
  }

  if (pathname.startsWith('/realtor/login') && hasRealtorSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/realtor/dashboard';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/portal/:path*', '/lender/:path*', '/crm/:path*', '/realtor/:path*'],
};
