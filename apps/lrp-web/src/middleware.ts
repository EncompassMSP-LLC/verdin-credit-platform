import { NextResponse, type NextRequest } from 'next/server';
import { CRM_SESSION_COOKIE } from '@/lib/crm/config';
import { LENDER_SESSION_COOKIE } from '@/lib/lender/config';
import { PLATFORM_ACCESS_COOKIE } from '@/lib/platform/config';

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
  const hasLenderSession = Boolean(request.cookies.get(LENDER_SESSION_COOKIE)?.value);

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
  const hasCrmSession = Boolean(request.cookies.get(CRM_SESSION_COOKIE)?.value);

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

  return NextResponse.next();
}

export const config = {
  matcher: ['/portal/:path*', '/lender/:path*', '/crm/:path*'],
};
