import { visit } from 'unist-util-visit';

export default function remarkWikiLink({ base = '' } = {}) {
  return (tree, file) => {
    const filePath = (file.history && file.history[0]) || file.path || '';
    const norm     = filePath.replace(/\\/g, '/');
    const m        = norm.match(/\/articles\/(ru|en)\//);
    const lang     = m ? m[1] : 'ru';

    visit(tree, 'text', (node, index, parent) => {
      const regex = /(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]/g;
      let match;
      const newNodes = [];
      let lastIndex = 0;

      while ((match = regex.exec(node.value)) !== null) {
        if (match.index > lastIndex) {
          newNodes.push({ type: 'text', value: node.value.slice(lastIndex, match.index) });
        }
        const id      = match[1].trim();
        const display = (match[2] || id).trim();
        newNodes.push({
          type: 'link',
          url: `${base}/${lang}/articles/${id}`,
          children: [{ type: 'text', value: display }],
        });
        lastIndex = match.index + match[0].length;
      }

      if (newNodes.length > 0) {
        if (lastIndex < node.value.length) {
          newNodes.push({ type: 'text', value: node.value.slice(lastIndex) });
        }
        parent.children.splice(index, 1, ...newNodes);
        return index + newNodes.length;
      }
    });
  };
}
