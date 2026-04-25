export function slugToTitle(slug: string): string {
  return slug.replace(/-/g, ' ');
}

export function idToTitle(id: string): string {
  const name = id.split('/').pop()!.replace(/\.mdx?$/, '');
  return name.replace(/-/g, ' ');
}
