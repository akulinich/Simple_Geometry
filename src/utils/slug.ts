export function slugToTitle(slug: string): string {
  return slug.replace(/-/g, ' ');
}
