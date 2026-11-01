# Fikra Automation — service details and consultation update

## Included
- Clicking a service card opens a full-screen service details view.
- The details view shows the service image/video, description, and active offers from `service_offers`.
- Offer cards show monthly, yearly, or one-time billing cadence, price, features, and the popular badge when `is_popular` is enabled.
- Selecting an offer opens the consultation form in a dialog and preselects the service and offer.
- A general consultation button is available in the request section and in each service details view.
- The existing validated form continues to insert into `public.leads`; it does not request a public SELECT permission.
- The Admin dashboard includes the consultation requests tab and reads lead records for authorized admins.
- The public visit counter UI, JavaScript calls, and related SQL setup snippet have been removed.
- Service card color and offer cadence/popular controls are included in Admin.
- French and Arabic pages are updated. Service-worker cache versions are bumped to v3.

## Supabase migration
Run `migration-catalogue-fields.sql` once in Supabase SQL Editor after uploading the matching files. It is additive: it adds optional catalogue columns and an admin-only SELECT policy for leads. It does not drop tables or existing rows.

## Important
The migration assumes the existing `public.is_admin()` function is already correctly configured for the site's admin account. Anonymous visitors keep INSERT-only access to `leads`. No live Supabase test was possible from this build environment.
